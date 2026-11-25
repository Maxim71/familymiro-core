# -*- coding: utf-8 -*-
import os
import re
import logging
from decimal import Decimal
from django.shortcuts import render, redirect, reverse
from django.conf import settings
from django.views.generic import View
from django.http import JsonResponse, HttpResponse
from django.db import models
from .services.pdf_ocr import extract_and_store_pages
from .services.spec_matcher import parse_specifications_and_create_requests

from .services.smart_router import resolve_section_and_brigade

import hashlib
from django.db.models import Q
from pypdf import PdfReader
import pytesseract
from django.contrib import messages

from django.contrib.auth import authenticate, login, logout
from .models import Document, ParsedPage, ItrStaff, WarehouseTmc, PurchaseRequest
from django.contrib.auth import authenticate, login, logout
from .models import Document, ParsedPage, ItrStaff, WarehouseTmc, PurchaseRequest

def resolve_section_and_brigade(section_code):
    code = str(section_code or "РД").upper().strip()
    return {"code": code, "title": f"Раздел {code}", "brigade": "Звено ПТО"}

logger = logging.getLogger(__name__)

pytesseract.pytesseract.tesseract_cmd = getattr(
    settings, 'TESSERACT_CMD', r'C:\Program Files\Tesseract-OCR\tesseract.exe'
)

# Коды томов: 24.0454-Р-ГП, 14-КЖ1, 61-ОВ1.ЦОД
CODE_RE = re.compile(
    r'^(?:\d{1,3}\s*[\.\)\|]?\s*)?([А-ЯЁA-Z0-9\.\-/]{2,25}-(?:Р|П)-[А-ЯЁA-Z0-9\.\-/]{1,20})\s*[\|\-–—:\s]+\s*(.{4,180})$',
    re.IGNORECASE
)


NAV_ITEMS = [
    {'name': 'Главная', 'url_name': 'storage_control:index_family'},
    {'name': 'О компании', 'url_name': '#'},
    {'name': 'Услуги', 'url_name': '#'},
    {'name': 'Блог', 'url_name': '#'},
    {'name': 'Контакты', 'url_name': '#'},
]


class AdvancedConstructionControlView(View):
    """Основной пульт управления: загрузка PDF, контроль ревизий SHA-256, фильтр и ведомость"""

    def get(self, request, *args, **kwargs):
        dossier_id = request.GET.get('dossier_id')
        if dossier_id:
            dossier_payload = {
                "step_1_code": "24.0454-Р-ГП",
                "step_2_material": "Геотекстиль Дорнит",
                "step_3_altitude": "0.000м (Репер)",
                "step_4_axes": "Оси 1-5 // А-Д",
                "step_6_passport": "Верифицирован (media/passports/65-CCK_Zavod.pdf)",
                "final_id_hash": dossier_id.upper()
            }
            return render(request, "storage_control/pto_dossier.html", {
                "dossier": dossier_payload,
                "nav_items": NAV_ITEMS
            })

        stock_list = WarehouseTmc.objects.filter(owner=current_owner).order_by('item_code')
        staff_list = ItrStaff.objects.filter(owner=current_owner).order_by('name')
        all_reqs = PurchaseRequest.objects.filter(document__owner=current_owner)

    # Изоляция рабочего пространства по владельцу (Multi-Tenant)
    def get(self, request, *args, **kwargs):
        current_owner = request.user if request.user.is_authenticated else None
        documents_list = Document.objects.filter(owner=current_owner).order_by('-uploaded_at')[:50]
        stock_list = WarehouseTmc.objects.filter(owner=current_owner).order_by('item_code')
        staff_list = ItrStaff.objects.filter(owner=current_owner).order_by('name')
        selected_doc_id = request.GET.get('doc_id')
        section_filter = (request.GET.get('section') or '').strip().upper()

        if selected_doc_id and selected_doc_id.isdigit():
            active_doc = Document.objects.filter(owner=current_owner, id=int(selected_doc_id)).first()
        else:
            active_doc = documents_list.first()

        parsed_data = []
        file_ok = False
        if active_doc and active_doc.file:
            try:
                file_ok = os.path.exists(active_doc.file.path)
            except (NotImplementedError, ValueError):
                file_ok = False

        if file_ok:
            for page in active_doc.pages.all():
                if not page.text:
                    continue
                for line in page.text.split("\n"):
                    m1 = CODE_RE.match(line.strip())
                    if m1:
                        c = m1.group(1).strip()
                        n = re.sub(r'[.\s_]{3,}', ' ', m1.group(2).strip())
                        if len(n) > 3:
                            if section_filter and section_filter not in c.upper() and section_filter not in n.upper():
                                continue
                            decoded = resolve_section_and_brigade(c)
                            parsed_data.append({
                                "code": c,
                                "name": decoded.get("section") or decoded.get("title") or n,
                                "snip_ref": decoded.get("snip_ref", "ГОСТ 21.1101-2013"),
                                "snip_url": decoded.get("snip_url", "https://cntd.ru"),
                                "brigade": decoded.get("brigade", "Звено ПТО"),
                                "duty": decoded.get("duty", "Монтаж по рабочей документации"),
                                "stage": "РД",
                            })

                                    # Группируем ведомость по профильным бригадам с указанием состава звена и ответственных
        brigade_groups = {}
        staff_by_idx = list(staff_list)

        for idx, item in enumerate(parsed_data):
            b_name = item["brigade"] or "Общестроительная бригада ПТО"
            if b_name not in brigade_groups:
                # Назначаем ответственного ИТР из базы и расчётную численность звена
                lead_staff = staff_by_idx[len(brigade_groups) % len(staff_by_idx)] if staff_by_idx else None
                lead_label = (
                    f"{lead_staff.name} [{lead_staff.staff_id}] ({lead_staff.role_type})"
                    if lead_staff else "Косарев М.В. [ITR-MAX-77] (Главный Архитектор)"
                )
                team_size = 6 if ("монолит" in b_name.lower() or "строител" in b_name.lower()) else 4
                brigade_groups[b_name] = {
                    "brigade_name": b_name,
                    "group_num": len(brigade_groups) + 1,
                    "leader": lead_label,
                    "team_size": team_size,
                    "items": [],
                }
            brigade_groups[b_name]["items"].append(item)


        err_msg = None if parsed_data else "Склад чертежей пуст или по фильтру нет позиций. Загрузите PDF-комплект ниже."
        purchase_requests = (
            PurchaseRequest.objects.filter(document=active_doc).order_by('record_type', 'id')
            if active_doc else []
        )

        all_reqs = PurchaseRequest.objects.filter(document__owner=current_owner)
        erp_b2b_stats = {
            "new_requests": all_reqs.filter(record_type="BUY", status="NEW").count(),
            "in_progress_b2b": all_reqs.filter(record_type="BUY", status__in=["IN_PROGRESS", "PAID"]).count(),
            "delivered_count": all_reqs.filter(record_type="BUY", status="DELIVERED").count(),
            "warehouse_positions": stock_list.count(),
        }

        total_docs = Document.objects.filter(owner=current_owner).count()
        work_docs = Document.objects.filter(owner=current_owner, work_status="WORK").count()
        crm_ceo_stats = {
            "total_docs": total_docs,
            "work_docs": work_docs,
            "readiness_pct": int((work_docs / total_docs) * 100) if total_docs else 0,
            "tep_volumes_count": all_reqs.filter(record_type="TEP").count(),
            "limits_count": all_reqs.filter(record_type="LIMIT").count(),
        }

        requested_goal = request.GET.get("goal", "")
        if not requested_goal:
            if brigade_groups:
                effective_goal = "BRIGADES"
            elif purchase_requests:
                effective_goal = "SUPPLY"
            else:
                effective_goal = "ALL"
        else:
            effective_goal = requested_goal

        from storage_control.services.route_tracer import build_engineering_procurement_rows
        purchase_requests = build_engineering_procurement_rows(purchase_requests)

        dynamic_tables = []
        if active_doc and getattr(active_doc, "file", None):
            try:
                from storage_control.services.grid_extractor import extract_geometric_tables
                geo = extract_geometric_tables(active_doc.file.path)
                dynamic_tables = [t for t in geo.get("tables", []) if not t.get("is_standard_spec")]
            except Exception:
                dynamic_tables = []

        return render(request, "storage_control/index.html", {
            "rows": parsed_data,
            "error": err_msg,
            "count": len(parsed_data),
            "nav_items": NAV_ITEMS,
            "staff_list": staff_list,
            "stock_list": stock_list,
            "purchase_requests": purchase_requests,
            "dynamic_tables": dynamic_tables,
            "documents_list": documents_list,
            "active_doc": active_doc,
            "section_filter": section_filter,
            "parse_goal": effective_goal,
            "brigade_groups": list(brigade_groups.values()),
            "erp_b2b_stats": erp_b2b_stats,
            "crm_ceo_stats": crm_ceo_stats,
        })

    def post(self, request, *args, **kwargs):
        current_owner = request.user if request.user.is_authenticated else None
        pdf_file = request.FILES.get('pdf_file')
        if not pdf_file:
            messages.warning(request, "Файл PDF не выбран.")
            return redirect(request.path)

        # Вычисляем SHA-256 загружаемого PDF для защиты от дублей
        hasher = hashlib.sha256()
        for chunk in pdf_file.chunks():
            hasher.update(chunk)
        current_hash = hasher.hexdigest()
        pdf_file.seek(0)

        # 1. Проверяем дубль SHA-256 строго внутри пространства текущего владельца
        existing_hash_doc = Document.objects.filter(owner=current_owner, file_hash=current_hash).first()
        if existing_hash_doc:
            doc = existing_hash_doc
            messages.info(
                request,
                f"Файл идентичен (SHA-256 совпадает) тому «{doc.title}» [Рев. {doc.revision_num}]. Дубль не создан, ведомость пересчитана."
            )
        else:
            # 2. Вычисляем номер следующей ревизии и архивируем старые версии только этого владельца
            prev_docs = Document.objects.filter(owner=current_owner, title=pdf_file.name)
            next_rev = (prev_docs.aggregate(models.Max('revision_num'))['revision_num__max'] or 0) + 1
            prev_docs.update(work_status='ARCHIVED')

            # 3. Создаём новую актуальную ревизию
            doc = Document.objects.create(
                title=pdf_file.name,
                file=pdf_file,
                file_hash=current_hash,
                revision_num=next_rev,
                work_status='WORK',
                owner=current_owner,
            )
            if next_rev > 1:
                messages.warning(
                    request,
                    f"Загружена новая ревизия №{next_rev} тома «{doc.title}»! Предыдущие версии аннулированы."
                )

        import threading
        from django.db import close_old_connections
        from .services.pdf_ocr import extract_and_store_pages
        from .services.spec_matcher import parse_specifications_and_create_requests

        staff_id = request.POST.get('selected_staff_id', '')
        staff_obj = ItrStaff.objects.filter(staff_id=staff_id).first()
        staff_label = f"{staff_obj.name} [{staff_obj.staff_id}]" if staff_obj else (staff_id or "Штаб ПТО")
        notify_tg = request.POST.get('notify_telegram') == '1'

        def _background_turbo_parse(target_doc_id: int, operator_label: str, do_tg: bool):
            close_old_connections()
            try:
                d_obj = Document.objects.filter(id=target_doc_id).first()
                if not d_obj:
                    return
                rep = extract_and_store_pages(d_obj)
                spec_rep = parse_specifications_and_create_requests(d_obj, staff_label=operator_label)
                if do_tg:
                    from .telegram_bot import send_pto_telegram_report
                    req_cnt = d_obj.purchase_requests.count() if hasattr(d_obj, 'purchase_requests') else 0
                    send_pto_telegram_report(operator_label, d_obj.title, rep.get("pages_processed", 0), req_cnt)
            finally:
                close_old_connections()

        threading.Thread(target=_background_turbo_parse, args=(doc.id, staff_label, notify_tg), daemon=True).start()
        messages.success(
            request,
            f"⚡ Том «{doc.title}» [Рев. {doc.revision_num}] принят в фоновый конвейер! Страницы, спецификации и узлы «Черепахи» появятся автоматически через несколько секунд."
        )

        return redirect(f"{reverse('storage_control:dashboard')}?doc_id={doc.id}")

class TrackerSearchAPIView(View):
    """Точечный поиск по картотеке РД, паспортам качества и складу с привязкой к листам PDF."""

    def get(self, request, *args, **kwargs):
        q = request.GET.get('q', '').strip()
        mode = request.GET.get('mode', 'all')
        current_owner = request.user if request.user.is_authenticated else None
        results = []

        if not q:
            return JsonResponse({'results': results})

        if mode in ('all', 'stock'):
            tmc_qs = WarehouseTmc.objects.filter(
                owner=current_owner
            ).filter(
                Q(nomenclature__icontains=q) | Q(item_code__icontains=q)
            )[:20]
            for item in tmc_qs:
                results.append({
                    'source': f"Склад: {item.item_code}",
                    'snippet': f"{item.nomenclature} — Остаток на складе: {item.stock_balance} {item.unit}",
                    'norm': 'Склад ТМЦ',
                    'folder_code': 'СКЛАД',
                    'pdf_url': '',
                    'page_number': 1,
                    'doc_id': None,
                })

        if mode in ('all', 'passport'):
            pages_qs = ParsedPage.objects.filter(
                document__owner=current_owner,
                text__icontains=q
            )
            if mode == 'passport':
                pages_qs = pages_qs.filter(
                    Q(text__icontains='паспорт') | Q(text__icontains='сертификат')
                )
            for page in pages_qs.select_related('document').order_by('document__title', 'page_number')[:40]:
                raw_txt = page.text or ""
                # Убираем штампы и разделяем склеенные слова для полного читаемого наименования
                clean_txt = re.sub(r'Формат\s*А\d(?:х\d)?', '', raw_txt, flags=re.IGNORECASE)
                clean_txt = re.sub(r'([а-яё])([А-ЯЁ])', r'\1 | \2', clean_txt)

                matched_lines = [
                    ln.strip() for ln in clean_txt.split('\n')
                    if q.lower() in ln.lower() and len(ln.strip()) > 3
                ]
                if matched_lines:
                    full_snippet = " — ".join(matched_lines[:3])[:380]
                else:
                    idx = clean_txt.lower().find(q.lower())
                    start = max(0, idx - 80)
                    full_snippet = clean_txt[start:start + 320].replace('\n', ' ').strip()

                doc_title = page.document.title
                folder_match = re.search(r'(\d{2}-[А-ЯЁA-Z0-9]+)', doc_title)
                folder_code = folder_match.group(1) if folder_match else doc_title[:12]
                norm_name = page.get_official_norm_name() if hasattr(page, 'get_official_norm_name') else folder_code
                pdf_url = page.document.file.url if page.document.file else ""

                results.append({
                    'source': f"{doc_title} (Лист №{page.page_number})",
                    'snippet': full_snippet,
                    'norm': norm_name,
                    'folder_code': folder_code,
                    'pdf_url': pdf_url,
                    'page_number': page.page_number,
                    'doc_id': page.document.id,
                })

        return JsonResponse({'results': results})

class PurchaseRequestAPIView(View):
    """Формирование и поиск заявок на закупку материалов по спецификации после парсинга"""

    def get(self, request, *args, **kwargs):
        q = request.GET.get('q', '').strip().lower()
        latest_doc = Document.objects.order_by('-uploaded_at').first()

        if not latest_doc:
            return JsonResponse({'requests': [], 'doc_title': 'Нет загруженных спецификаций'})

        spec_re = re.compile(
            r'([А-ЯЁA-Z][А-ЯЁа-яёA-Za-z0-9\s\-\.\(\)\/]{4,80}?)\s+'
            r'(м2|м²|м3|м³|шт\.?|т|кг|п\.м\.|м)\s+'
            r'(\d+(?:[\.,]\d+)?)',
            re.IGNORECASE
        )

        warehouse_items = list(WarehouseTmc.objects.all())
        aggregated = {}

        for page in latest_doc.pages.all():
            if not page.text:
                continue
            for line in page.text.split('\n'):
                m = spec_re.search(line.strip())
                if not m:
                    continue
                name = re.sub(r'\s+', ' ', m.group(1)).strip()
                unit = m.group(2).strip()
                qty = Decimal(m.group(3).replace(',', '.'))

                if q and q not in name.lower():
                    continue

                key = name.lower()
                if key not in aggregated:
                    aggregated[key] = {
                        'material': name,
                        'unit': unit,
                        'required': Decimal('0'),
                        'page': page.page_number,
                    }
                aggregated[key]['required'] += qty

        purchase_list = []
        for key, item in aggregated.items():
            stock_match = next(
                (w for w in warehouse_items if w.nomenclature.lower() in key or key in w.nomenclature.lower()),
                None
            )
            in_stock = stock_match.stock_balance if stock_match else Decimal('0')
            to_buy = max(Decimal('0'), item['required'] - in_stock)

            purchase_list.append({
                'material': item['material'],
                'unit': item['unit'],
                'required': float(item['required']),
                'in_stock': float(in_stock),
                'to_buy': float(to_buy),
                'status': 'ЗАКУПИТЬ' if to_buy > 0 else 'ЕСТЬ НА СКЛАДЕ',
                'source': f"Стр. {item['page']}"
            })

        return JsonResponse({
            'doc_title': latest_doc.title,
            'requests': purchase_list
        })

from django.db.models import Q


def parse_trigger(request):
    """Расширенный поиск: ищет сразу и на складе ТМЦ, и в тексте чертежей"""
    name = request.GET.get('product_name', '').strip()
    if not name:
        return JsonResponse({'message': 'Введите название материала'}, status=400)

    # 1. Ищем на складе (твой старый код)
    found_stock = WarehouseTmc.objects.filter(nomenclature__icontains=name)[:10]
    items = [
        {
            'nomenclature': t.nomenclature,
            'stock': str(t.stock_balance),
            'unit': t.unit,
        }
        for t in found_stock
    ]

    # 2. Ищем в распознанных листах PDF (новое расширение)
    found_pages = ParsedPage.objects.select_related('document').filter(
        text__icontains=name
    ).order_by('-id')[:10]

    pages = []
    for p in found_pages:
        idx = p.text.lower().find(name.lower())
        start = max(0, idx - 30)
        snippet = p.text[start:start + 100].replace('\n', ' ').strip()
        pages.append({
            'doc_title': p.document.title,
            'page_number': p.page_number,
            'snippet': f"...{snippet}...",
        })

    return JsonResponse({
        'message': f'Найдено по запросу «{name}»: склад ({len(items)}), чертежи ({len(pages)})',
        'items': items,
        'pages': pages,
    })

def export_staff_excel_view(request):
    """Скачивание 3-листового штабного Excel (Снабжение, ПТО, Логистика)."""
    from .services.export_staff_excel import build_staff_excel_bytes

    doc_id = request.GET.get("doc_id")
    doc = Document.objects.filter(id=int(doc_id)).first() if (doc_id and doc_id.isdigit()) else None

    xlsx_bytes = build_staff_excel_bytes(doc=doc)
    filename = f"Shtab_PTO_Snabzhenie_{doc.id if doc else 'ALL'}.xlsx"

    response = HttpResponse(
        xlsx_bytes,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response

def export_customer_gpr_view(request):
    """Скачивание внешнего Календарного графика для Заказчика (ГПР .xlsx)."""
    from .services.export_customer_gpr import build_customer_gpr_excel

    doc_id = request.GET.get("doc_id")
    parsed_id = int(doc_id) if (doc_id and doc_id.isdigit()) else None

    xlsx_bytes = build_customer_gpr_excel(doc_id=parsed_id)
    filename = f"Grafik_GPR_Zakazchik_{parsed_id if parsed_id else 'FULL_PROJECT'}.xlsx"

    response = HttpResponse(
        xlsx_bytes,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response

def export_aosr_docx_view(request):
    """Генерация и скачивание готового Акта освидетельствования скрытых работ (АОСР .docx)."""
    from .services.export_aosr import build_aosr_docx_bytes

    doc_id = request.GET.get("doc_id")
    doc = Document.objects.filter(id=int(doc_id)).first() if (doc_id and doc_id.isdigit()) else Document.objects.order_by("-uploaded_at").first()
    if not doc:
        messages.warning(request, "Сначала загрузите том РД для формирования АОСР.")
        return redirect("storage_control:dashboard")

    handover_mode = request.GET.get("handover_mode", "GEN_TO_CUSTOMER")
    date_start = request.GET.get("date_start", "")
    date_end = request.GET.get("date_end", "")
    executor_name = (request.GET.get("executor_name") or "").strip() or "Косарев М.В. (Главный Архитектор / ПТО)"
    inspector_name = (request.GET.get("inspector_name") or "").strip() or "Представитель строительного контроля Заказчика"
    next_work = (request.GET.get("next_work") or "").strip() or "производство последующих работ согласно графику ГПР"

    docx_bytes = build_aosr_docx_bytes(
        doc=doc,
        handover_mode=handover_mode,
        date_start=date_start,
        date_end=date_end,
        executor_name=executor_name,
        inspector_name=inspector_name,
        next_work_allowed=next_work,
    )

    response = HttpResponse(
        docx_bytes,
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    response["Content-Disposition"] = f'attachment; filename="AOSR_Tom_{doc.id}.docx"'
    return response
def mark_passport_view(request):
    from storage_control.services.mark_passport import build_mark_passport_data
    from storage_control.services.turtle_geometry import extract_scaled_node_cuts_from_pdf
    from .models import PhotoIntake, ParsedPage, Document
    from django.db.models import Q
    import re as _re

    q = (request.GET.get("q") or "").strip()
    ctx = build_mark_passport_data(q)

    photos = list(PhotoIntake.objects.all()[:15])
    ctx["field_photos"] = photos

    turtle_plans = []
    for ph in photos[:6]:
        tp = (ph.payload_1c_json or {}).get("turtle_plan")
        if tp and tp.get("ok") and tp.get("svg_preview"):
            tp_copy = dict(tp)
            tp_copy["photo_id"] = ph.id
            turtle_plans.append(tp_copy)
    ctx["turtle_plans"] = turtle_plans

    milled_cuts = []
    selected_doc_id = (request.GET.get("doc_id") or "").strip()
    clean_q = _re.sub(r'\s*[Ll]\s*=.*$', '', q).strip()
    q_compact = clean_q.replace(" ", "")

    pages_qs = ParsedPage.objects.select_related("document").all()
    if selected_doc_id.isdigit():
        pages_qs = pages_qs.filter(document_id=int(selected_doc_id))
        matched_pages = list(pages_qs.filter(Q(text__icontains="Узел") | Q(text__icontains="1:20") | Q(text__icontains="1:10") | Q(text__icontains="Спецификация")).order_by("page_number")[:2])
        if not matched_pages:
            matched_pages = list(pages_qs.order_by("-page_number")[:1])
    elif clean_q:
        page_filter = Q(text__icontains=clean_q) | Q(text__icontains=q_compact)
        matched_pages = list(pages_qs.filter(page_filter).order_by("-document__uploaded_at", "page_number")[:2])
    else:
        matched_pages = list(pages_qs.filter(Q(text__icontains="Узел") | Q(text__icontains="1:20")).order_by("-document__uploaded_at", "page_number")[:2])

    by_doc = {}
    for mp in matched_pages:
        if mp.document and mp.document.file and os.path.exists(mp.document.file.path):
            by_doc.setdefault(mp.document, []).append(mp.page_number)

    for doc_obj, p_nums in list(by_doc.items())[:1]:
        cuts = extract_scaled_node_cuts_from_pdf(doc_obj.file.path, doc_obj.id, p_nums[:1], query_hint=clean_q or "Узел")
        for c in cuts:
            c["doc_id"] = doc_obj.id
            c["doc_title"] = doc_obj.title
            milled_cuts.append(c)

    ctx["milled_cuts"] = milled_cuts
    ctx["selected_doc_id"] = selected_doc_id
    ctx["available_docs"] = list(Document.objects.order_by("-uploaded_at").values("id", "title")[:15])

    return render(request, "storage_control/mark_passport.html", ctx)

    # Авто-вырезка «Черепахой-Фрезой» узлов с масштабами (М 1:10, М 1:20, М 1:50...) по найденным листам РД
    from django.db.models import Q
    milled_cuts = []
    q_compact = q.replace(" ", "")
    page_filter = Q(text__icontains=q) | Q(text__icontains=q_compact) if q else Q(text__icontains="1:20")
    matched_pages = ParsedPage.objects.select_related("document").filter(page_filter)[:4]
    if not matched_pages:
        matched_pages = ParsedPage.objects.select_related("document").filter(text__icontains="1:20")[:3]

    by_doc = {}
    for mp in matched_pages:

        if mp.document and mp.document.file and os.path.exists(mp.document.file.path):
            by_doc.setdefault(mp.document, []).append(mp.page_number)
    for doc_obj, p_nums in list(by_doc.items())[:2]:
        cuts = extract_scaled_node_cuts_from_pdf(doc_obj.file.path, doc_obj.id, p_nums, query_hint=q or "М 1:20")
        for c in cuts:
            c["doc_title"] = doc_obj.title
            milled_cuts.append(c)
    ctx["milled_cuts"] = milled_cuts

    return render(request, "storage_control/mark_passport.html", ctx)


def export_dynamic_table_view(request):
    """Выгружает выбранную нестандартную таблицу чертежа (отделка, экспликация, журнал) в чистый Excel (.xlsx)."""
    import io
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from django.http import HttpResponse, Http404
    from django.core.cache import cache

    doc_id = request.GET.get("doc_id")
    idx = int(request.GET.get("idx", 0))
    doc = Document.objects.filter(id=doc_id).first()
    if not doc or not getattr(doc, "file", None):
        raise Http404("Документ не найден")

    c_key = f"geo_dyn_tables_v2_{doc.id}"
    tables = cache.get(c_key)
    if tables is None:
        from storage_control.services.grid_extractor import extract_geometric_tables
        geo = extract_geometric_tables(doc.file.path, max_pages=12)
        tables = [t for t in geo.get("tables", []) if not t.get("is_standard_spec")]
        cache.set(c_key, tables, 3600)

    if idx < 0 or idx >= len(tables):
        raise Http404("Таблица не найдена")

    dt = tables[idx]
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Лист_{dt['page']}_{dt['schema_code']}"[:31]

    hdr_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    hdr_font = Font(name="Calibri", size=11, bold=True, color="FFD700")
    thin = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1"),
    )

    ws.append(dt["headers"])
    for c_i in range(1, len(dt["headers"]) + 1):
        cell = ws.cell(row=1, column=c_i)
        cell.fill = hdr_fill
        cell.font = hdr_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin
        ws.column_dimensions[openpyxl.utils.get_column_letter(c_i)].width = 24

    for row in dt["rows"]:
        ws.append(row)
        r_num = ws.max_row
        for c_i in range(1, len(dt["headers"]) + 1):
            c_obj = ws.cell(row=r_num, column=c_i)
            c_obj.border = thin
            c_obj.alignment = Alignment(vertical="center", wrap_text=True)

    buf = io.BytesIO()
    wb.save(buf)
    resp = HttpResponse(
        buf.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    resp["Content-Disposition"] = f'attachment; filename="table_{doc.id}_p{dt["page"]}.xlsx"'
    return resp

def mark_passport_seo_alias_view(request, slug):
    """SEO-ЧПУ алиас /marka/<slug>/ -> открывает Паспорт Марки без крякозябр в URL."""
    from django.http import QueryDict
    clean_q = slug.replace("-", " ").strip()
    qd = QueryDict(mutable=True)
    qd["q"] = clean_q
    request.GET = qd
    return mark_passport_view(request)


def async_search_api_view(request):
    """Асинхронный JSON-поиск по картотеке РД и складу (для мгновенных подсказок и SEO)."""
    from django.http import JsonResponse
    q = request.GET.get("q", "").strip()
    if len(q) < 2:
        return JsonResponse({"ok": True, "query": q, "count": 0, "results": []})
    pages = ParsedPage.objects.select_related("document").filter(text__icontains=q)[:15]
    results = [
        {
            "doc_title": p.document.title if p.document else "РД",
            "page": p.page_number,
            "snippet": (p.text or "")[:180].replace("\n", " "),
            "passport_url": f"/mark-passport/?q={q}",
        }
        for p in pages
    ]
    return JsonResponse({"ok": True, "query": q, "count": len(results), "results": results})

def mark_passport_seo_alias_view(request, slug):
    from django.http import QueryDict
    from .templatetags.seo_tags import make_seo_slug

    clean_slug = make_seo_slug(slug)
    matched_title = slug.replace("-", " ").strip()
    for mat_name in PurchaseRequest.objects.values_list("material_name", flat=True).distinct()[:500]:
        if make_seo_slug(mat_name) == clean_slug or clean_slug in make_seo_slug(mat_name):
            matched_title = mat_name
            break

    qd = QueryDict(mutable=True)
    qd["q"] = matched_title
    request.GET = qd
    return mark_passport_view(request)


def async_search_api_view(request):
    from django.http import JsonResponse
    from .templatetags.seo_tags import make_seo_slug

    q = request.GET.get("q", "").strip()
    if len(q) < 2:
        return JsonResponse({"ok": True, "query": q, "count": 0, "results": []})
    pages = ParsedPage.objects.select_related("document").filter(text__icontains=q)[:15]
    results = [
        {
            "doc_title": p.document.title if p.document else "РД",
            "page": p.page_number,
            "snippet": (p.text or "")[:180].replace("\n", " "),
            "passport_url": f"/marka/{make_seo_slug(q)}/",
        }
        for p in pages
    ]
    return JsonResponse({"ok": True, "query": q, "count": len(results), "results": results})


def photo_1c_hub_view(request):
    from .models import PhotoIntake
    from .services.falcon_vision import analyze_field_photo
    from .services.one_c_bridge import extract_1c_document_payload, build_photo_catalog_answer
    from .services.turtle_geometry import analyze_building_plan_footprint

    if request.method == "POST" and request.FILES.get("image"):
        kind = request.POST.get("photo_kind", "UPD_INVOICE")
        scene = request.POST.get("scene_mode", "AUTO")
        notes = request.POST.get("notes", "").strip()
        obj = PhotoIntake.objects.create(
            photo_kind=kind,
            image=request.FILES["image"],
            uploaded_by=request.user.username if request.user.is_authenticated else "ПТО Штаб",
            notes=notes[:250],
        )
        vision = analyze_field_photo(obj.image.path, manual_hint_text=notes, scene_mode=scene)
        payload_1c = extract_1c_document_payload(vision)
        payload_1c["catalog_answer"] = build_photo_catalog_answer(vision, payload_1c)
        payload_1c["turtle_plan"] = analyze_building_plan_footprint(obj.image.path, operator_object_title=notes)
        codes_txt = ", ".join(f"{c['type']}:{c['raw'][:30]}" for c in vision.get("codes_found", []))

        obj.scene_label = vision.get("scene_info", {}).get("scene_label", "")
        obj.sharpness_pct = vision.get("sharpness_after_pct", 0.0)
        obj.barcode_summary = codes_txt[:250]
        obj.detected_axes = vision.get("detected_axes", "")[:115]
        obj.detected_elevation = vision.get("detected_elevation", "")[:55]
        obj.supplier_inn = payload_1c.get("supplier_inn", "")[:20]
        obj.doc_number = payload_1c.get("doc_number", "")[:115]
        obj.ocr_raw_text = vision.get("ocr_preview", "")
        obj.payload_1c_json = payload_1c
        obj.save()

    return redirect(request.POST.get("return_to") or "/marka/truba-pe-110/")



def photo_1c_accept_view(request, pk):
    from .models import PhotoIntake
    from .services.one_c_bridge import commit_1c_intake_to_warehouse_and_log
    if request.method == "POST":
        obj = get_object_or_404(PhotoIntake, pk=pk)
        operator = request.user.username if request.user.is_authenticated else "ПТО Штаб"
        commit_1c_intake_to_warehouse_and_log(obj.payload_1c_json or {}, operator=operator)
        obj.status = "ACCEPTED_1C"
        obj.save(update_fields=["status"])
    return redirect(request.META.get("HTTP_REFERER") or "/marka/truba-pe-110/")


def photo_1c_export_view(request, pk, fmt):
    from .models import PhotoIntake
    from .services.one_c_bridge import build_1c_exchange_files
    obj = get_object_or_404(PhotoIntake, pk=pk)
    xlsx_bytes, xml_bytes = build_1c_exchange_files(obj.payload_1c_json or {})
    if fmt == "xml":
        resp = HttpResponse(xml_bytes, content_type="application/xml; charset=utf-8")
        resp["Content-Disposition"] = f'attachment; filename="1C_UPD_{obj.id}.xml"'
        return resp
    resp = HttpResponse(
        xlsx_bytes,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    resp["Content-Disposition"] = f'attachment; filename="1C_Prihod_M4_{obj.id}.xlsx"'
    return resp

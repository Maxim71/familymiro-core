
def _norm_x_variants(q: str) -> list[str]:
    base = (q or "").strip()
    if not base:
        return []
    import re
    v_ru = re.sub(r'(?<=\d)[xX\u00d7\*](?=\d)', '\u0445', base)
    v_en = re.sub(r'(?<=\d)[\u0445\u0425\u00d7\*](?=\d)', 'x', base)
    v_mul = re.sub(r'(?<=\d)[xX\u0445\u0425\*](?=\d)', '\u00d7', base)
    return list(dict.fromkeys([base, v_ru, v_en, v_mul]))
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

        from storage_control.services.building_twin import build_building_twin_index
        return render(request, "storage_control/index.html", {
            "building_twin": build_building_twin_index(),
            "exec_kpi": __import__("storage_control.services.id_template_engine", fromlist=["build_executive_site_dashboard"]).build_executive_site_dashboard(),
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

def _enrich_mark_passport_ctx(ctx: dict, query: str) -> dict:
    from storage_control.models import StockMovement, PurchaseRequest, PhotoIntake
    from storage_control.services.turtle_geometry import (
        build_contextual_cad_modes, build_project_axes_and_floor_cuts, build_nss_cable_vector_svg
    )
    ctx["cad_modes"] = build_contextual_cad_modes(mark_query=str(ctx.get("query") or request.GET.get("q") or ""))
    ctx["project_floor_cuts"] = build_project_axes_and_floor_cuts()
    ctx["nss_vector_svg"] = build_nss_cable_vector_svg(mark_query=query)
    from storage_control.services.turtle_geometry import extract_real_building_metrics_from_pdfs
    ctx["real_metrics"] = extract_real_building_metrics_from_pdfs()
    ctx["stock_movements"] = list(StockMovement.objects.select_related("purchase_request", "photo_intake").all()[:15])
    ctx["gpr_positions"] = list(PurchaseRequest.objects.order_by("-id").values("id", "material_name", "required_qty", "unit")[:40])
    from storage_control.services.building_twin import build_building_twin_index
    ctx["building_twin"] = build_building_twin_index()

    all_intakes = list(PhotoIntake.objects.order_by("-id")[:120])
    ctx["recent_5_intakes"] = all_intakes[:5]
    ctx["archived_intakes"] = all_intakes[5:]
    ctx["total_intakes_count"] = len(all_intakes)

    return ctx

def mark_passport_view(request):
    query = str(request.GET.get("q") or "")
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

    from .models import StockMovement, PurchaseRequest
    from storage_control.services.turtle_geometry import build_contextual_cad_modes
    ctx["cad_modes"] = build_contextual_cad_modes(mark_query=str(ctx.get("query") or request.GET.get("q") or ""))
    ctx["stock_movements"] = list(StockMovement.objects.select_related("purchase_request", "photo_intake").all()[:15])
    ctx["gpr_positions"] = list(PurchaseRequest.objects.order_by("-id").values("id", "material_name", "required_qty", "unit")[:40])
    from storage_control.services.building_twin import build_building_twin_index
    ctx["building_twin"] = build_building_twin_index()
    ctx = _enrich_mark_passport_ctx(ctx, str(ctx.get("query") or request.GET.get("q") or ""))
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

    from .models import StockMovement, PurchaseRequest
    from storage_control.services.turtle_geometry import build_contextual_cad_modes
    ctx["cad_modes"] = build_contextual_cad_modes(mark_query=str(ctx.get("query") or request.GET.get("q") or ""))
    ctx["stock_movements"] = list(StockMovement.objects.select_related("purchase_request", "photo_intake").all()[:15])
    ctx["gpr_positions"] = list(PurchaseRequest.objects.order_by("-id").values("id", "material_name", "required_qty", "unit")[:40])
    from storage_control.services.building_twin import build_building_twin_index
    ctx["building_twin"] = build_building_twin_index()
    ctx = _enrich_mark_passport_ctx(ctx, str(ctx.get("query") or request.GET.get("q") or ""))
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


from django.views.decorators.http import require_POST


@require_POST
def stock_movement_create_view(request):
    from storage_control.services.stock_acts import register_stock_movement
    return_to = request.POST.get("return_to") or reverse("storage_control:dashboard")
    pr_raw = (request.POST.get("purchase_request_id") or "").strip()
    ph_raw = (request.POST.get("photo_intake_id") or "").strip()
    try:
        qty_val = float((request.POST.get("qty") or "0").replace(",", ".").strip())
    except ValueError:
        qty_val = 0.0

    mv, alerts = register_stock_movement(
        movement_kind=(request.POST.get("movement_kind") or "OUT_M11").strip(),
        material_name=(request.POST.get("material_name") or "").strip(),
        qty=qty_val,
        unit=(request.POST.get("unit") or "\u0448\u0442.").strip(),
        purchase_request_id=int(pr_raw) if pr_raw.isdigit() else None,
        photo_intake_id=int(ph_raw) if ph_raw.isdigit() else None,
        upd_batch_number=(request.POST.get("upd_batch_number") or "").strip(),
        brigade_or_subcontractor=(request.POST.get("brigade_or_subcontractor") or "").strip(),
        axes_and_ojr=(request.POST.get("axes_and_ojr") or "").strip(),
        responsible_itr=(request.POST.get("responsible_itr") or "\u0428\u0442\u0430\u0431 \u041f\u0422\u041e").strip(),
        doc_status=(request.POST.get("doc_status") or "CONFIRMED").strip(),
    )
    messages.success(request, f"\u041e\u0444\u043e\u0440\u043c\u043b\u0435\u043d \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442 \u2116{mv.id}: {mv.get_movement_kind_display()} ({mv.qty} {mv.unit}).")
    for al in alerts:
        messages.warning(request, al)
    return redirect(return_to)


@require_POST
def stock_movement_status_view(request, movement_id: int):
    from storage_control.models import StockMovement
    mv = get_object_or_404(StockMovement, id=movement_id)
    new_status = (request.POST.get("doc_status") or "CONFIRMED").strip()
    if new_status in {c for c in StockMovement.DOC_STATUS_CHOICES}:
        mv.doc_status = new_status
        mv.save(update_fields=["doc_status"])
    return redirect(request.POST.get("return_to") or reverse("storage_control:dashboard"))


def stock_movement_print_view(request, movement_id: int):
    from storage_control.models import StockMovement
    mv = get_object_or_404(StockMovement, id=movement_id)

    standards_map = {
        "IN_UPD": ("????????? ????? ? ?-4", "???? 0315003 ? ????????????? ??????????? ?? ? 71? / ??? ?? ?? ? 1137 (???)"),
        "OUT_M11": ("??????????-????????? ? ?-11", "???? 0315006 ? ????????????? ??????????? ?? ? 71? (??????? / ???)"),
        "OUT_M15_SUB": ("????????? ?? ?????? ?????????? ?? ??????? ? ?-15 (???????????? ?????)", "???? 0315007 ? ????????????? ??????????? ?? ? 71? (??? / ?????????)"),
        "RET_M11": ("????????? ?? ??????? ???????? ?????????? ?? ????? (???????? ?-11)", "???? 0315006 ? ????????????? ??????????? ?? ? 71? (???)"),
        "DEFECT_TORG2": ("??? ?? ????????????? ??????????? ?? ?????????? ? ???????? ? ????-2", "???? 0330202 ? ????????????? ??????????? ?? ? 132 (????????????? / ???)"),
        "WRITE_OFF_AOSR": ("??? ??????????????????? ??????? ????? (????) ? ???????? ??? (?-29)", "?????? ???????? ?? ? 344/?? ? ???? ? 70108-2022 ? ?????? ???????? ? 883? (???? / ???)"),
    }
    title_str, norm_str = standards_map.get(mv.movement_kind, (mv.get_movement_kind_display(), "???????? ??"))
    doc_ref = mv.purchase_request.document.title if (mv.purchase_request and mv.purchase_request.document) else "??????? ???????????? (??)"
    legal_note = (
        "????????? ???????? ?????????? ?? ???????????? ???????? ??? ???????? ????? ?????????????. ???????? ????????????? ?????? ?? ?????????????? (?-29) ??? ?????????? ??-2 / ??-3."
        if mv.movement_kind == "OUT_M15_SUB"
        else "?????? ????????? ? ???????????? ? ????????? ?????????????, ?? ? ???????????? ?????? ????? (?????? ???????? ?? ? 883?, ?????????? ?? ?? ?? ? 2464 ????????)."
    )

    html = f"""<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8"><title>{title_str} ?{mv.id}</title>
    <style>
        body{{font-family:'Times New Roman',serif;padding:24px 32px;color:#000;font-size:13px;line-height:1.4}}
        .okud{{text-align:right;font-size:11px;border:1px solid #000;display:inline-block;padding:4px 8px;float:right}}
        h2{{margin:8px 0 4px 0;font-size:16px;text-transform:uppercase;clear:both}}
        .sub{{font-size:11px;color:#333;margin-bottom:12px;border-bottom:1.5px solid #000;padding-bottom:6px}}
        table{{width:100%;border-collapse:collapse;margin:12px 0}}
        th,td{{border:1px solid #000;padding:6px 8px;font-size:12px}}
        th{{background:#f3f4f6;text-align:center}}
        .box{{border:1px solid #000;padding:8px;margin:10px 0;font-size:12px}}
        .signs{{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:24px;font-size:12px}}
        @media print{{.no-print{{display:none}}}}
    </style></head><body>
    <div class="no-print" style="margin-bottom:14px;font-family:Arial,sans-serif;">
        <button onclick="window.print()" style="padding:9px 18px;font-size:13px;font-weight:bold;cursor:pointer;">??? ?????? ???????????? ?????? ?4 / ????????? PDF</button>
    </div>
    <div class="okud">{norm_str}</div>
    <h2>{title_str} ? {mv.id}</h2>
    <div class="sub">???? ???????????: <strong>{mv.created_at:%d.%m.%Y}</strong> ? ?????? ?????????: <strong>{mv.get_doc_status_display()}</strong> ? ???? ??: <strong>{doc_ref}</strong></div>
    <div class="box">
        <div><strong>1. ????????? / ?????? ??? ? ?????????? ????????:</strong> {mv.upd_batch_number or '???????? ????????? ?? ? ???????? ????????'}</div>
        <div><strong>2. ???????, ???, ??????? ? ?????? ? ??? (??-11-05-2007):</strong> {mv.axes_and_ojr or '?? ???????? ??????? ???????????? ????? (???)'}</div>
        <div><strong>3. ?????????? / ??????????? ????? (??????? / ????????????):</strong> {mv.brigade_or_subcontractor or '??????? ??????? ?????????????'}</div>
        <div><strong>4. ?????? ????? (??? / ??????? ? 883?):</strong> ??????? ?????????? ?? ?? ?? ? 2464 ????????; ?????? ? ??????? ????????.</div>
    </div>
    <table>
        <thead><tr><th>? ?/?</th><th>???????????? ??? / ????????????</th><th>??. ???.</th><th>??????????</th><th>??????? ??? / ?????</th><th>?????????? (???? / ??-123)</th></tr></thead>
        <tbody><tr><td style="text-align:center;">1</td><td>{mv.material_name}</td><td style="text-align:center;">{mv.unit}</td><td style="text-align:center;"><strong>{mv.qty}</strong></td><td>{mv.purchase_request.material_name if mv.purchase_request else '????????? ????'}</td><td>????????????? ??</td></tr></tbody>
    </table>
    <p style="font-size:11.5px;"><em>{legal_note}</em></p>
    <div class="signs">
        <div><strong>???? (????????? / ????????? ???????):</strong><br><br>_____________________ / {mv.responsible_itr} /<br><span style="font-size:10px;">(?????????, ???????, ???????????, ? ??? ???????)</span></div>
        <div><strong>?????? ({mv.brigade_or_subcontractor or '?????? / ????????'}):</strong><br><br>_____________________ / ___________________ /<br><span style="font-size:10px;">(?????????, ???????, ???????????, ????????????/??????)</span></div>
        <div><strong>????????????? ????????????? (????????? ?????????):</strong><br><br>_____________________ / ___________________ /<br><span style="font-size:10px;">(???????, ?????, ? ??? ??????/???????)</span></div>
        <div><strong>????????? ?????? (??? ??????????????????? ????):</strong><br><br>_____________________ / ___________________ /<br><span style="font-size:10px;">(???????, ????)</span></div>
    </div>
    </body></html>"""
    return HttpResponse(html)


def room_passport_view(request, room_code: str):
    from storage_control.services.building_twin import build_single_room_passport
    ctx = build_single_room_passport(room_code)
    return render(request, "storage_control/room_passport.html", ctx)


def save_object_passport_view(request):
    from django.http import JsonResponse
    from storage_control.services.id_template_engine import save_object_passport, get_saved_object_passport
    if request.method == "POST":
        saved = save_object_passport(request.POST.dict())
        return JsonResponse({"ok": True, "passport": saved})
    return JsonResponse({"ok": True, "passport": get_saved_object_passport()})


def id_registry_export_view(request):
    import io, openpyxl
    from django.http import HttpResponse
    from django.utils import timezone
    from storage_control.services.id_template_engine import build_filled_customer_registry_xlsx
    if request.GET.get("demo") == "1" and request.session.get("demo_sandbox_file"):
        dr = request.session["demo_sandbox_file"]
        today_str = timezone.localdate().strftime("%d.%m.%Y")
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "\u0420\u0435\u0435\u0441\u0442\u0440_\u0418\u0414_\u0414\u0435\u043c\u043e"
        ws.append([f"\u0420\u0415\u0415\u0421\u0422\u0420 \u0418\u0414 \u0418 \u0412\u0415\u0414\u041e\u041c\u041e\u0421\u0422\u042c \u0420\u0410\u0411\u041e\u0422 \u041f\u041e \u0424\u0410\u0419\u041b\u0423: {dr.get('filename', '')}"])
        ws.append(["\u2116 \u043f/\u043f", "\u041d\u0430\u0438\u043c\u0435\u043d\u043e\u0432\u0430\u043d\u0438\u0435 \u043f\u043e\u0437\u0438\u0446\u0438\u0438 / \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u0430", "\u0412\u044b\u0441\u043e\u0442\u043d\u044b\u0435 \u043e\u0442\u043c\u0435\u0442\u043a\u0438", "\u041e\u0441\u0438 / \u0418\u0441\u0442\u043e\u0447\u043d\u0438\u043a", "\u0414\u0430\u0442\u0430 \u0444\u043e\u0440\u043c\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f"])
        ws.append([1, f"\u0410\u041e\u0421\u0420 (\u041f\u0440\u0438\u043a\u0430\u0437 \u2116 344/\u043f\u0440) \u043f\u043e \u043a\u043e\u043c\u043f\u043b\u0435\u043a\u0442\u0443: {dr.get('filename', '')}", dr.get("elevs", ""), dr.get("axes", ""), today_str])
        for i, ln in enumerate(dr.get("lines", []), start=2):
            ws.append([i, ln, dr.get("elevs", ""), dr.get("filename", ""), today_str])
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        thin = Side(style="thin", color="CBD5E1")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)
        ws["A1"].font = Font(bold=True, size=12, color="0F172A")
        for col_let, w in [("A", 8), ("B", 64), ("C", 24), ("D", 32), ("E", 18)]:
            ws.column_dimensions[col_let].width = w
        for cell in ws[2]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="1E3A8A")
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, max_col=5):
            for c in row:
                c.border = border
                c.alignment = Alignment(vertical="center", wrap_text=True)
        buf = io.BytesIO()
        wb.save(buf)
        resp = HttpResponse(buf.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        resp["Content-Disposition"] = 'attachment; filename="Reestr_ID_Novyy_Klient.xlsx"'
        return resp
    tpl_bytes = request.FILES["customer_xlsx"].read() if (request.method == "POST" and "customer_xlsx" in request.FILES) else None
    memo_txt = request.FILES["memo_file"].read().decode("utf-8", errors="ignore") if (request.method == "POST" and "memo_file" in request.FILES) else ""
    xlsx_data = build_filled_customer_registry_xlsx(template_bytes=tpl_bytes, memo_text=memo_txt)
    resp = HttpResponse(xlsx_data, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    resp["Content-Disposition"] = 'attachment; filename="Reestr_ID_344pr.xlsx"'
    return resp


def new_client_wizard_view(request):
    import re
    from django.shortcuts import redirect
    from storage_control.services.id_template_engine import save_object_passport
    from storage_control.models import Document, ParsedPage, PurchaseRequest, StockMovement, PhotoIntake
    demo_result = None
    if request.method == "POST":
        if "demo_any_file" in request.FILES:
            f = request.FILES["demo_any_file"]
            fname = f.name
            ext = fname.rsplit(".", 1)[-1].lower() if "." in fname else ""
            raw = f.read()
            extracted_lines = []
            pages_cnt = 1
            if ext == "pdf":
                import io, pypdf
                reader = pypdf.PdfReader(io.BytesIO(raw))
                pages_cnt = len(reader.pages)
                txt = "\n".join((p.extract_text() or "") for p in reader.pages[:30])
                txt = re.sub(r"([?-???-???])\n([?-???-???])", r"\1\2", txt)
                extracted_lines = [ln.strip() for ln in txt.splitlines() if len(ln.strip()) > 6][:12]
            elif ext in ("xlsx", "xls"):
                import io, openpyxl
                wb = openpyxl.load_workbook(io.BytesIO(raw), data_only=True)
                pages_cnt = len(wb.sheetnames)
                for row in wb.active.iter_rows(values_only=True):
                    vals = [str(v).strip() for v in row if v is not None and str(v).strip()]
                    if vals:
                        extracted_lines.append(" | ".join(vals[:5]))
                    if len(extracted_lines) >= 12:
                        break
            elif ext == "docx":
                import io, docx
                d = docx.Document(io.BytesIO(raw))
                extracted_lines = [p.text.strip() for p in d.paragraphs if p.text.strip()][:12]
            else:
                extracted_lines = [f"\u0413\u0440\u0430\u0444\u0438\u0447\u0435\u0441\u043a\u0438\u0439 \u043b\u0438\u0441\u0442 / \u0444\u043e\u0442\u043e ({ext.upper()}), \u0440\u0430\u0437\u043c\u0435\u0440 {round(len(raw)/1024, 1)} \u041a\u0411 \u2014 \u0433\u043e\u0442\u043e\u0432\u043e \u043a \u0432\u0435\u043a\u0442\u043e\u0440\u043d\u043e\u0439 \u043a\u0430\u043b\u0438\u0431\u0440\u043e\u0432\u043a\u0435 \u0427\u0435\u0440\u0435\u043f\u0430\u0445\u0438 CAD \u0438 \u043f\u0440\u0438\u0451\u043c\u043a\u0435 \u0423\u041f\u0414 \u0421\u043e\u043aолом."]

            joined = " ".join(extracted_lines)
            elevs = sorted(set(re.findall(r'[+\-]\d[\.,]\d{3}', joined)))[:6]
            axes = sorted(set(re.findall(r'(?:\u043e\u0441[\u0438\u044f\u0445]|\u043e\u0441\u044c)\s+[0-9\u0410-\u042fA-Z\-\/]{1,12}', joined, re.I)))[:6]
            demo_result = {
                "filename": fname,
                "ext": ext.upper(),
                "pages_cnt": pages_cnt,
                "elevs": ", ".join(elevs) or "\u041e\u043f\u0440\u0435\u0434\u0435\u043b\u044f\u044e\u0442\u0441\u044f \u043f\u043e \u043f\u0430\u0441порту \u043eбъекта",
                "axes": ", ".join(axes) or "\u0413\u043eтов\u043e \u043a \u043f\u0440\u0438вязке \u043a \u0441етке \u043eсей",
                "lines": extracted_lines or ["\u0424\u0430\u0439\u043b \u0443спе\u0448\u043d\u043e \u043f\u0440\u0438\u043d\u044f\u0442 \u0438 \u0433\u043e\u0442\u043e\u0432 \u043a \u0432\u044b\u043f\u0443\u0441\u043a\u0443 АОСР № 344/пр \u0438 р\u0435\u0435стр\u0430 ИД."],
            }
            request.session["demo_sandbox_file"] = demo_result
            return render(request, "storage_control/new_client.html", {"demo_result": demo_result})

        save_object_passport(request.POST.dict())
        if request.POST.get("wipe_old_data") == "1":
            StockMovement.objects.all().delete()
            PurchaseRequest.objects.all().delete()
            ParsedPage.objects.all().delete()
            Document.objects.all().delete()
            PhotoIntake.objects.all().delete()
        return redirect("storage_control:dashboard")
    return render(request, "storage_control/new_client.html", {"demo_result": demo_result})


def operation_memo_export_view(request):
    from django.http import HttpResponse
    from storage_control.services.id_template_engine import build_operation_memo_docx_bytes
    data = build_operation_memo_docx_bytes()
    resp = HttpResponse(data, content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    resp["Content-Disposition"] = 'attachment; filename="Pamyatka_Ekspluatacii_i_Garantii.docx"'
    return resp


def _suggest_analog_for_material(name: str) -> str:
    low = (name or "").lower()
    if "\u0449\u0435\u0431\u0435\u043d" in low:
        return "\u0410\u043d\u0430\u043b\u043e\u0433: \u0449\u0435\u0431\u0435\u043d\u044c \u0433\u0440\u0430\u043d\u0438\u0442\u043d\u044b\u0439/\u0433\u0440\u0430\u0432\u0438\u0439\u043d\u044b\u0439 \u0442\u043e\u0439 \u0436\u0435 \u0444\u0440\u0430\u043a\u0446\u0438\u0438 (\u0413\u041e\u0421\u0422 8267-93) + \u043f\u0430\u0441\u043f\u043e\u0440\u0442 \u043a\u0430\u0447\u0435\u0441\u0442\u0432\u0430"
    if any(k in low for k in ("\u0440\u043e\u0437\u0435\u0442\u043a", "\u0432\u044b\u043a\u043b\u044e\u0447")):
        return "\u0410\u043d\u0430\u043b\u043e\u0433: \u0441\u0442\u0440\u043e\u0433\u043e \u0441 \u0442\u043e\u0439 \u0436\u0435 \u0441\u0442\u0435\u043f\u0435\u043d\u044c\u044e IP (IP20/IP44/IP54), 16\u0410 \u0438 \u0442\u0438\u043f\u043e\u043c \u043c\u043e\u043d\u0442\u0430\u0436\u0430"
    if any(k in low for k in ("\u043b\u0430\u043c\u043f", "\u0441\u0432\u0435\u0442\u0438\u043b", "\u0431\u0440\u0430")):
        return "\u0410\u043d\u0430\u043b\u043e\u0433: \u043f\u043e \u0441\u0432\u0435\u0442\u043e\u0432\u043e\u043c\u0443 \u043f\u043e\u0442\u043e\u043a\u0443 (\u043b\u043c), \u0446\u043e\u043a\u043e\u043b\u044e (E27/GU10/LED), \u0442\u0435\u043c\u043f\u0435\u0440\u0430\u0442\u0443\u0440\u0435 3000/4000K \u0438 IP"
    if "\u043c\u0438\u043d" in low or "\u0432\u0430\u0442\u0430" in low:
        return "\u0410\u043d\u0430\u043b\u043e\u0433: \u043f\u043b\u0438\u0442\u044b \u043c\u0438\u043d\u0435\u0440\u0430\u043b\u043e\u0432\u0430\u0442\u043d\u044b\u0435 \u041d\u0413 \u0442\u043e\u0439 \u0436\u0435 \u043f\u043b\u043e\u0442\u043d\u043e\u0441\u0442\u0438 (75\u2013120 \u043a\u0433/\u043c\u00b3) \u0438 \u0442\u043e\u043b\u0449\u0438\u043d\u044b (Rockwool / \u0422\u0435\u0445\u043d\u043e\u041d\u0418\u041a\u041e\u041b\u042c / ISOROC, \u0413\u041e\u0421\u0422 9573-2012)"
    if "\u0440\u0430\u0434\u0438\u0430\u0442\u043e\u0440" in low:
        return "\u0410\u043d\u0430\u043b\u043e\u0433: \u043f\u043e \u043c\u043e\u0449\u043d\u043e\u0441\u0442\u0438 (\u0412\u0442), \u043c\u0435\u0436\u043e\u0441\u0435\u0432\u043e\u043c\u0443 \u0440\u0430\u0441\u0441\u0442\u043e\u044f\u043d\u0438\u044e (350/500 \u043c\u043c) \u0438 \u0434\u0430\u0432\u043b\u0435\u043d\u0438\u044e (\u0413\u041e\u0421\u0422 31311)"
    return "\u0410\u043d\u0430\u043b\u043e\u0433: \u043f\u043e \u0413\u041e\u0421\u0422/\u0421\u041f \u0447\u0435\u0440\u0435\u0437 \u043b\u0438\u0441\u0442 \u0430\u0432\u0442\u043e\u0440\u0441\u043a\u043e\u0433\u043e \u043d\u0430\u0434\u0437\u043e\u0440\u0430 \u0441 \u043f\u0440\u043e\u0435\u043a\u0442\u0438\u0440\u043e\u0432\u0449\u0438\u043a\u043e\u043c"


def project_totals_and_analogs_api(request):
    import re, functools
    from django.http import JsonResponse
    from django.db.models import Q
    from storage_control.models import PurchaseRequest, ParsedPage
    from storage_control.services.building_twin import fix_autocad_mojibake

    q = (request.GET.get("q") or "").strip()
    if not q:
        return JsonResponse({"ok": True, "items": [], "totals_by_unit": {}, "pdf_mentions": []})
    variants = _norm_x_variants(q)
    stem = q[:max(4, len(q) - 2)] if len(q) >= 5 else q
    if stem not in variants:
        variants.append(stem)

    cond = functools.reduce(lambda a, b: a | b, [Q(material_name__icontains=v) for v in variants])
    reqs = list(PurchaseRequest.objects.select_related("document").filter(cond).order_by("id")[:150])

    grouped, totals_by_unit = {}, {}
    for r in reqs:
        key = f"{(r.material_name or '').strip()} | {(r.floor_info or '\u041f\u043e \u043f\u0440\u043e\u0435\u043a\u0442\u0443').strip()}"
        u = (r.unit or "\u0448\u0442.").strip()
        qty = float(r.required_qty or 0)
        totals_by_unit[u] = round(totals_by_unit.get(u, 0.0) + qty, 2)
        entry = grouped.setdefault(key, {
            "req_num": f"\u0417\u041c-{r.id:04d}",
            "mark_name": (r.material_name or "").strip(),
            "floor_or_zone": (r.floor_info or "\u041f\u043e \u043f\u043b\u0430\u043d\u0443 \u0420\u0414").strip(),
            "doc_title": r.document.title if r.document else "\u0420\u0414",
            "qty": 0.0,
            "unit": u,
        })
        entry["qty"] = round(entry["qty"] + qty, 2)

    pdf_mentions = []
    p_cond = functools.reduce(lambda a, b: a | b, [Q(text__icontains=v) for v in variants])
    for pg in ParsedPage.objects.select_related("document").filter(p_cond)[:12]:
        txt = fix_autocad_mojibake(pg.text or "")
        idx = txt.lower().find(stem.lower())
        if idx >= 0:
            snip = re.sub(r'\s+', ' ', txt[max(0, idx - 35): idx + 110]).strip()
            pdf_mentions.append({"doc": pg.document.title if pg.document else "\u0420\u0414", "page": pg.page_number, "snippet": snip})

    return JsonResponse({"ok": True, "query": q, "totals_by_unit": totals_by_unit, "items": list(grouped.values()), "pdf_mentions": pdf_mentions, "general_analog": _suggest_analog_for_material(q)})


def inventory_foreman_api(request):
    import os, json
    from django.conf import settings
    from django.http import JsonResponse
    fpath = os.path.join(settings.BASE_DIR, "foreman_inventory.json")
    items = json.load(open(fpath, encoding="utf-8")) if os.path.exists(fpath) else []
    if request.method == "POST":
        inv_num = f"\u0418\u041d\u0412-{len(items) + 1:04d}"
        rec = {
            "inv_num": inv_num,
            "item_name": (request.POST.get("item_name") or "").strip(),
            "qty": (request.POST.get("qty") or "1").strip(),
            "foreman": (request.POST.get("foreman") or "\u041f\u0440\u043e\u0440\u0430\u0431 \u0443\u0447\u0430\u0441\u0442\u043a\u0430").strip(),
            "zone": (request.POST.get("zone") or "\u0423\u0447\u0430\u0441\u0442\u043e\u043a \u043c\u043e\u043d\u043e\u043b\u0438\u0442\u0430").strip(),
            "invoice_check": (request.POST.get("invoice_check") or "\u0421\u0432\u0435\u0440\u0435\u043d\u043e \u043f\u043e \u0444\u043e\u0442\u043e \u0423\u041f\u0414 \u0438 \u0444\u0430\u043a\u0442\u0443").strip(),
        }
        if rec["item_name"]:
            items.insert(0, rec)
            json.dump(items, open(fpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return JsonResponse({"ok": True, "items": items})


def room_cascade_dynamics_api(request):
    import datetime
    from django.http import JsonResponse
    from django.utils import timezone
    from storage_control.models import PurchaseRequest, PhotoIntake

    room_code = (request.GET.get("code") or "101").strip()
    room_name = (request.GET.get("name") or "\u041a\u043e\u0440\u0438\u0434\u043e\u0440").strip()
    area = (request.GET.get("area") or "45.0").strip()
    today = timezone.localdate()

    # ????????? ?????????? ?? ??????? ????????? ?? 3 ?????????? ??????? ??? ???? ???????
    finishing, cables_trays, pipes_mep = [], [], []
    for r in PurchaseRequest.objects.order_by("-required_qty")[:120]:
        nm = (r.material_name or "").strip()
        low = nm.lower()
        row = {"req_num": f"\u0417\u041c-{r.id:04d}", "name": nm[:85], "plan": f"{r.required_qty} {r.unit}", "deficit": f"{r.deficit_qty} {r.unit}"}
        if any(k in low for k in ("\u043f\u0433\u043f", "\u043f\u043b\u0438\u0442", "\u0448\u0442\u0443\u043a\u0430\u0442", "\u043a\u0440\u0430\u0441\u043a", "\u043f\u043e\u043b", "\u0434\u0432\u0435\u0440", "\u0432\u0430\u0442\u0430")):
            if len(finishing) < 5: finishing.append(row)
        elif any(k in low for k in ("\u043a\u0430\u0431\u0435\u043b", "\u043b\u043e\u0442\u043e\u043a", "\u043b\u043e\u0442\u043a", "\u043f\u0440\u043e\u0432\u043e\u0434", "\u0431\u044d", "\u0449\u0438\u0442", "\u0440\u043e\u0437\u0435\u0442")):
            if len(cables_trays) < 5: cables_trays.append(row)
        elif any(k in low for k in ("\u0442\u0440\u0443\u0431", "\u0432\u043e\u0437\u0434\u0443\u0445", "\u0442\u0440\u0430\u043f", "\u043a\u043b\u0430\u043f\u0430\u043d", "\u043d\u0430\u0441\u043e\u0441")):
            if len(pipes_mep) < 5: pipes_mep.append(row)

    # ?????????? ???? ?????? ????? ?????????
    tag = f"ROOM:{room_code}"
    photos = []
    for ph in PhotoIntake.objects.filter(notes__icontains=tag).order_by("-id")[:12]:
        photos.append({
            "id": ph.id,
            "url": ph.image.url if ph.image else "",
            "date": ph.created_at.strftime("%d.%m.%Y %H:%M") if getattr(ph, "created_at", None) else today.strftime("%d.%m.%Y"),
            "report": ph.ocr_raw_text or ph.notes or "\u0424\u043e\u0442\u043e-\u0444\u0438\u043a\u0441\u0430\u0446\u0438\u044f \u0441\u043c\u0435\u043d\u044b",
        })

    progress_pct = min(100, len(photos) * 25)
    return JsonResponse({
        "ok": True,
        "room_code": room_code,
        "room_name": room_name,
        "area": area,
        "progress_pct": progress_pct,
        "finish_date": (today + datetime.timedelta(days=max(3, 20 - len(photos) * 4))).strftime("%d.%m.%Y"),
        "finishing": finishing,
        "cables_trays": cables_trays,
        "pipes_mep": pipes_mep,
        "photos": photos,
    })


def room_photo_upload_api(request):
    from django.http import JsonResponse
    from storage_control.models import PhotoIntake
    if request.method == "POST" and "room_photo" in request.FILES:
        code = (request.POST.get("room_code") or "101").strip()
        name = (request.POST.get("room_name") or "\u041a\u043e\u0440\u0438\u0434\u043e\u0440").strip()
        work_note = (request.POST.get("work_note") or "").strip()
        f = request.FILES["room_photo"]
        # ?????? ???? ??????? ?????? (??????????? ???? ????? ?? ?????/?????????/OCR)
        detected = work_note or "\u0417\u0440\u0435\u043d\u0438\u0435 \u0441\u043e\u043a\u043e\u043b\u0430: \u0437\u0430\u0444\u0438\u043a\u0441\u0438\u0440\u043e\u0432\u0430\u043d \u043c\u043e\u043d\u0442\u0430\u0436 \u043b\u043e\u0442\u043a\u043e\u0432, \u043f\u0440\u043e\u043a\u043b\u0430\u0434\u043a\u0430 \u043a\u0430\u0431\u0435\u043b\u044f \u0438 \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u043e \u041f\u0413\u041f / \u043e\u0442\u0434\u0435\u043b\u043a\u0438 (+25% \u043a \u0433\u043e\u0442\u043e\u0432\u043d\u043e\u0441\u0442\u0438)"
        ph = PhotoIntake.objects.create(
            image=f,
            doc_number=f"\u0424\u041e\u0422\u041e-{code}",
            notes=f"ROOM:{code} | \u041f\u043e\u043c. {code} ({name})",
            ocr_raw_text=detected,
        )
        return JsonResponse({"ok": True, "photo_id": ph.id})
    return JsonResponse({"ok": False}, status=400)

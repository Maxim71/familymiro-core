# -*- coding: utf-8 -*-
import re
from decimal import Decimal
from storage_control.models import Document, PurchaseRequest, WarehouseTmc, BimCrossLink


def _map_doc_discipline(title: str) -> str:
    t = (title or "").upper()
    if any(k in t for k in ("-Р“Рџ", "Р“Рџ.", "Р“Р•РќРџР›РђРќ")):
        return "GP"
    if any(k in t for k in ("-РђР ", "РђР .", "-РђР")):
        return "AR"
    if any(k in t for k in ("-РљР–", "-РљР ", "-РљРњ", "РљР–.")):
        return "KJ"
    if any(k in t for k in ("-Р­РЎ", "-Р­Рћ", "-Р­Рњ", "Р­РЎ.")):
        return "ES"
    if any(k in t for k in ("-РРўРџ", "-РћР’", "РРўРџ.", "РћР’.")):
        return "OV"
    if any(k in t for k in ("-Р’Рљ", "-РќР’Рљ", "Р’Рљ.")):
        return "VK"
    if any(k in t for k in ("-РђРЎРЈ", "-РђРљ", "-РЎРЎ")):
        return "SS"
    return "GP"


def run_automatic_bim_collision_audit() -> dict:
    """РђРІС‚РѕРјР°С‚РёС‡РµСЃРєРёР№ РєСЂРѕСЃСЃ-Р°СѓРґРёС‚ РјРµР¶РґСѓ Р·Р°РіСЂСѓР¶РµРЅРЅС‹РјРё С‚РѕРјР°РјРё Р Р” Рё РЎРєР»Р°РґРѕРј РўРњР¦."""
    docs = list(Document.objects.prefetch_related("pages").all())
    if not docs:
        return {"total_links": 0, "collisions": 0, "matched": 0}

    docs_by_disc = {}
    for d in docs:
        disc = _map_doc_discipline(d.title)
        full_text = "\n".join(f"[Р›.{p.page_number}] {p.text or ''}" for p in d.pages.all())
        full_text = re.sub(r'(Рђ?РџРІ)\s*\|\s*(Р‘РЁРІ)', r'\1\2', full_text, flags=re.IGNORECASE)
        full_text = re.sub(r'(\d)\s*Рє\s*\|\s*(Р’С‚|Р’)\b', r'\1 Рє\2', full_text, flags=re.IGNORECASE)
        docs_by_disc.setdefault(disc, []).append((d, full_text))

    BimCrossLink.objects.exclude(link_status="RESOLVED").delete()
    stats = {"total_links": 0, "collisions": 0, "matched": 0}

    def _register_link(bim_tag, axes_elev, src_disc, src_doc, src_page, src_qty, tgt_disc, tgt_doc, tgt_page, tgt_qty, status, note, assigned):
        req = PurchaseRequest.objects.filter(document=src_doc, material_name__icontains=bim_tag[:14]).first()
        wh = WarehouseTmc.objects.filter(nomenclature__icontains=bim_tag[:14]).first()
        BimCrossLink.objects.create(
            bim_tag=bim_tag[:120],
            axes_and_elevation=axes_elev[:120],
            source_discipline=src_disc,
            source_document=src_doc,
            source_page=src_page,
            source_qty=src_qty,
            target_discipline=tgt_disc,
            target_document=tgt_doc,
            target_page=tgt_page,
            target_qty=tgt_qty,
            warehouse_qty=wh.stock_balance if wh else Decimal("0"),
            purchase_request=req,
            link_status=status,
            engineering_note=note,
            assigned_to=assigned,
        )
        stats["total_links"] += 1
        if status == "COLLISION":
            stats["collisions"] += 1
        elif status == "MATCHED":
            stats["matched"] += 1

    # --- РџР РђР’РР›Рћ 1: Р“Рџ в†” РљР– (Р’РІРѕРґС‹ С‚СЂСѓР± РїСЂРѕС‚РёРІ Р·Р°РєР»Р°РґРЅС‹С… РіРёР»СЊР· РІ С„СѓРЅРґР°РјРµРЅС‚Р°С…) ---
    kj_docs = docs_by_disc.get("KJ", [])
    for gp_doc, gp_text in docs_by_disc.get("GP", []):
        seen_pipes = set()
        for m in re.finditer(r'((?:С‚СЂ\.\s*РџРќР”|С‚СЂ\.\s*РџР­|Р’С‹РїСѓСЃРє\s+Рљ1)[^\n,;]{2,40})', gp_text, re.IGNORECASE):
            pipe_label = re.sub(r'\s+', ' ', m.group(1)).strip()
            diam_m = re.search(r'[ГГё]\s*(\d{2,3})', pipe_label)
            diam = diam_m.group(1) if diam_m else ""
            sig = f"{pipe_label[:20].lower()}:{diam}"
            if sig in seen_pipes:
                continue
            seen_pipes.add(sig)

            matched_kj = next(
                (kd for kd, kt in kj_docs if diam and re.search(rf'(?:РіРёР»СЊР·|РѕС‚РІРµСЂСЃС‚|Р·Р°РєР»Р°РґРЅ|РїСЂРѕРµРј|РїСЂРѕС‘Рј|Г\s*{diam})', kt, re.I)),
                None,
            )
            if matched_kj:
                _register_link(
                    f"Р’РІРѕРґ {pipe_label}", "РћС‚Рј. РІРІРѕРґР° РїРѕ Р“Рџ / Р¤СѓРЅРґР°РјРµРЅС‚ РљР–",
                    "GP", gp_doc, 7, Decimal("1"), "KJ", matched_kj, 1, Decimal("1"),
                    "MATCHED", f"вњ… Р’РІРѕРґ В«{pipe_label}В» РїРѕРґС‚РІРµСЂР¶РґС‘РЅ Р·Р°РєР»Р°РґРЅС‹РјРё РІ {matched_kj.title}.", "РџСЂРѕСЂР°Р± РљР– / РќР’Рљ"
                )
            elif kj_docs:
                first_kj = kj_docs[0][0]
                _register_link(
                    f"Р’РІРѕРґ {pipe_label}", "РџРµСЂРµСЃРµС‡РµРЅРёРµ С„СѓРЅРґР°РјРµРЅС‚РЅРѕР№ РїР»РёС‚С‹ / СЃС‚РµРЅ РїРѕРґРІР°Р»Р°",
                    "GP", gp_doc, 7, Decimal("1"), "KJ", first_kj, 1, Decimal("0"),
                    "COLLISION", f"вљ пёЏ РљРћР›Р›РР—РРЇ Р“Рџ в†” РљР–: Р’ {gp_doc.title} Р·Р°Р»РѕР¶РµРЅ РІРІРѕРґ В«{pipe_label}В», РЅРѕ РІ {first_kj.title} РЅРµС‚ РіРёР»СЊР·С‹ Г{diam or 'РІРІРѕРґР°'}.", "Р“РРџ / РџСЂРѕСЂР°Р± РљР–"
                )
        # --- РџР РђР’РР›Рћ 2: Р“Рџ в†” Р­РЎ (РќР°СЂСѓР¶РЅС‹Рµ РєР°Р±РµР»СЊРЅС‹Рµ Р»РёРЅРёРё 0,4 РєР’ РїСЂРѕС‚РёРІ С‚РѕРјР° Р­РЎ) ---
    es_docs = docs_by_disc.get("ES", [])
    for gp_doc, gp_text in docs_by_disc.get("GP", []):
        seen_cables = set()
        for m in re.finditer(r'((?:Рђ?РџРІР‘РЁРІ|Р’Р’Р“|РђР’Р‘РЁРІ)[^\n,;вЂ”]{4,35})', gp_text, re.IGNORECASE):
            cab = re.sub(r'\s+', ' ', m.group(1)).strip()
            sec_m = re.search(r'(\d\s*[xС…Г—]\s*\d{2,3})', cab)
            sec = re.sub(r'\s+', '', sec_m.group(1)).lower() if sec_m else cab[:12].lower()
            if sec in seen_cables:
                continue
            seen_cables.add(sec)

            found_es = next((ed for ed, et in es_docs if sec in re.sub(r'\s+', '', et).lower()), None)
            if found_es:
                _register_link(
                    f"РљР› 0,4 РєР’ {cab}", "РўСЂР°СЃСЃР° РўРџ-13 / Р”Р“РЈ в†’ Р’Р РЈ Р·РґР°РЅРёСЏ",
                    "GP", gp_doc, 7, Decimal("1"), "ES", found_es, 1, Decimal("1"),
                    "MATCHED", f"вњ… РљР°Р±РµР»СЊРЅР°СЏ Р»РёРЅРёСЏ В«{cab}В» СЃ РїР»Р°РЅР° Р“Рџ СѓРІСЏР·Р°РЅР° СЃ С‚РѕРјРѕРј {found_es.title}.", "Р‘СЂРёРіР°РґР° Р­РћРњ / Р­РЎ"
                )
            elif es_docs:
                first_es = es_docs[0][0]
                _register_link(
                    f"РљР› 0,4 РєР’ {cab}", "РўСЂР°СЃСЃР° РўРџ-13 / Р”Р“РЈ в†’ Р’РІРѕРґ РІ Р·РґР°РЅРёРµ",
                    "GP", gp_doc, 7, Decimal("1"), "ES", first_es, 1, Decimal("0"),
                    "COLLISION", f"вљ пёЏ РљРћР›Р›РР—РРЇ Р“Рџ в†” Р­РЎ: РљР°Р±РµР»СЊ В«{cab}В» РёР· {gp_doc.title} РЅРµ РЅР°Р№РґРµРЅ РІ {first_es.title}.", "Р“Р»Р°РІРЅС‹Р№ СЌРЅРµСЂРіРµС‚РёРє"
                )

    # --- РџР РђР’РР›Рћ 3: РРўРџ / РћР’РёРљ в†” Р­РЎ (РЎРёР»РѕРІС‹Рµ РЅР°СЃРѕСЃС‹ Рё РїСЂРёРІРѕРґС‹ РїСЂРѕС‚РёРІ СЌР»РµРєС‚СЂРѕСЃРЅР°Р±Р¶РµРЅРёСЏ) ---
    for ov_doc, ov_text in docs_by_disc.get("OV", []):
        seen_pumps = set()
        for m in re.finditer(r'((?:РЅР°СЃРѕСЃ|РєР»Р°РїР°РЅ\s+Р·Р°РїРѕСЂРЅРѕ-СЂРµРіСѓР»РёСЂСѓСЋС‰РёР№)[^\n]{5,65}?N\s*=\s*(\d+(?:[\.,]\d+)?)\s*РєР’С‚)', ov_text, re.IGNORECASE):
            eq_name = re.sub(r'\s+', ' ', m.group(1)).strip()
            kw_val = Decimal(m.group(2).replace(',', '.'))
            if eq_name[:22].lower() in seen_pumps:
                continue
            seen_pumps.add(eq_name[:22].lower())

            target_es = es_docs[0][0] if es_docs else None
            es_has_itp = bool(es_docs and re.search(r'(?:РРўРџ|РЅР°СЃРѕСЃ|Р©РЎРЈ|Р©Рћ)', es_docs, re.IGNORECASE))
            status = "MATCHED" if es_has_itp else ("COLLISION" if target_es else "INFO")
            note = (
                f"вњ… Р­Р»РµРєС‚СЂРѕСЃРЅР°Р±Р¶РµРЅРёРµ В«{eq_name}В» ({kw_val} РєР’С‚) РїРѕРґС‚РІРµСЂР¶РґРµРЅРѕ РІ {target_es.title}."
                if es_has_itp
                else f"вљ пёЏ РџР РћР’Р•Р РљРђ РРўРџ в†” Р­РЎ: РџРѕС‚СЂРµР±РёС‚РµР»СЊ В«{eq_name}В» ({kw_val} РєР’С‚) С‚СЂРµР±СѓРµС‚ РїСЂРѕРІРµСЂРєРё С‰РёС‚Р°/РєР°Р±РµР»СЏ РІ {target_es.title if target_es else 'СЂР°Р·РґРµР»Рµ Р­РЎ'}."
            )
            _register_link(
                eq_name[:80], "РџРѕРјРµС‰РµРЅРёРµ РРўРџ / РџРѕРґРІР°Р»",
                "OV", ov_doc, 16, kw_val, "ES", target_es, 1 if target_es else None, kw_val if es_has_itp else Decimal("0"),
                status, note, "РџРўРћ Р­РћРњ + РћР’РёРљ"
            )

    # === Р”РћР‘РђР’Р›РЇР•Рњ РќРћР’Р«Р• РџР РђР’РР›Рђ РЎР’Р•Р РљР РќРР–Р• (РЅР°РїСЂРёРјРµСЂ: РђР  в†” РћР’, РљР– в†” Р­РЎ) ===

    return stats


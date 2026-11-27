import os, re, csv, io, json
from datetime import date
from django.conf import settings

RELAY_STATE_PATH = os.path.join(settings.BASE_DIR, "price_relay_cache.json")


def step_price_relay(batch_percent: int = 10) -> dict:
    """?????????? ?????????? ??????? ?????????????? ?????? ??? ?? ???????? ?? ?? (??? ?????????? ????)."""
    from storage_control.models import PurchaseRequest
    from storage_control.services.quantum_normalizer import canon_key

    state = json.load(open(RELAY_STATE_PATH, encoding="utf-8")) if os.path.exists(RELAY_STATE_PATH) else {"cursor": 0, "passes": 0, "prices": {}}
    reqs = list(PurchaseRequest.objects.order_by("id")[:1000])
    total = len(reqs)
    verified_cnt = sum(1 for r in reqs if canon_key(r.material_name) in state.get("prices", {}))
    cov = min(100, round((verified_cnt / total) * 100, 1)) if total else 0
    if batch_percent > 0 and total > 0:
        state["passes"] = state.get("passes", 0) + 1
        state["cursor"] = (state.get("cursor", 0) + max(1, (total * batch_percent) // 100)) % total
        json.dump(state, open(RELAY_STATE_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return {"passes": state.get("passes", 0), "coverage_pct": cov, "verified_cnt": verified_cnt, "total_cnt": total, "prices": state.get("prices", {})}


def import_dealer_csv(raw_bytes: bytes, source_label: str = "") -> int:
    """??????????? ?????? ???????? ???? ?? ?????-????? ?????? (.csv) ? ????????? ????????? ? ????."""
    from storage_control.services.quantum_normalizer import canon_key
    state = json.load(open(RELAY_STATE_PATH, encoding="utf-8")) if os.path.exists(RELAY_STATE_PATH) else {"cursor": 0, "passes": 0, "prices": {}}
    text = raw_bytes.decode("utf-8-sig", errors="ignore")
    reader = csv.reader(io.StringIO(text), delimiter=";" if ";" in text else ",")
    added = 0
    src_name = source_label or "Прайс-лист дилера (CSV)"
    for row in reader:
        if len(row) < 2:
            continue
        nm = row.strip()
        m_p = re.search(r'\d+(?:[\.,]\d+)?', row.replace(" ", "").replace(",", "."))
        if nm and m_p and float(m_p.group(0)) > 0:
            ck = canon_key(nm)
            state["prices"][ck] = {
                "name": nm[:90],
                "unit_price": round(float(m_p.group(0)), 2),
                "source": src_name,
                "updated": str(date.today()),
            }
            added += 1
    json.dump(state, open(RELAY_STATE_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return added

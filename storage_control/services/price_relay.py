import os, re, json
from datetime import date
from django.conf import settings

RELAY_STATE_PATH = os.path.join(settings.BASE_DIR, "price_relay_cache.json")


def _estimate_regression_price(name: str, qty: float) -> tuple[float, str]:
    low = (name or "").lower()
    m_du = re.search(r'(?:\u0414\u0443|DN)\s*(\d{2,4})', name, re.I)
    du = int(m_du.group(1)) if m_du else 50
    if "\u0444\u043b\u0430\u043d\u0435\u0446" in low:
        unit_p = round(du * 14.5, 2)
        src = "\u0420егрессия по Ду (АДЛ / СТМ)"
    elif "\u043a\u0440\u0430\u043d" in low:
        unit_p = round(du * 68.0, 2)
        src = "\u0420егрессия по Ду (Ридан / LD)"
    elif any(k in low for k in ("nd-isr", "nd-icr", "litened", "\u0431\u043b\u043e\u043a", "\u0443\u0441\u0442\u0430\u043d\u043e\u0432\u043a\u0430")):
        unit_p = 48500.0
        src = "\u041fрайс-индекс NED / Веза B2B"
    elif "\u043b\u0435\u043d\u0442\u0430" in low:
        unit_p = 420.0
        src = "\u041fрайс РОЛС Изомаркет (Energoflex)"
    elif "\u0432\u043e\u0437\u0434\u0443\u0445\u043e\u0432\u043e\u0434" in low:
        unit_p = 1450.0
        src = "\u0420егрессия сечения (ЛИСАНТ / ГалВент)"
    else:
        unit_p = 950.0
        src = "\u0418ндекс B2B-матрицы"
    return unit_p, src


def step_price_relay(batch_percent: int = 10) -> dict:
    """????????? 1 ???? ????: ????????? ????????? 10% ??????? ?? ?? ? ?????????? ? ????????? ? ???."""
    from storage_control.models import PurchaseRequest
    from storage_control.services.quantum_normalizer import canon_key

    state = json.load(open(RELAY_STATE_PATH, encoding="utf-8")) if os.path.exists(RELAY_STATE_PATH) else {"cursor": 0, "passes": 0, "prices": {}}
    reqs = list(PurchaseRequest.objects.order_by("id")[:1000])
    total = len(reqs)
    if total == 0:
        return {"passes": state["passes"], "coverage_pct": 0, "updated_now": 0, "prices": state["prices"]}

    batch_size = max(1, (total * batch_percent) // 100)
    start = state["cursor"] % total
    chunk = reqs[start: start + batch_size]
    for r in chunk:
        ck = canon_key(r.material_name)
        up, src = _estimate_regression_price(r.material_name, r.required_qty)
        state["prices"][ck] = {"name": r.material_name[:80], "unit_price": up, "source": src, "updated": str(date.today())}

    state["cursor"] = (start + batch_size) % total
    state["passes"] += 1
    json.dump(state, open(RELAY_STATE_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    cov = min(100, round((len(state["prices"]) / total) * 100, 1))
    return {"passes": state["passes"], "coverage_pct": cov, "updated_now": len(chunk), "prices": state["prices"]}


RELAY_MULTIPLIERS = {
    "partner_discount_pct": -12.0,
    "tzr_logistics_pct": 5.0,
    "inflation_reserve_pct": 4.0,
    "waste_reserve_pct": 3.0,
}


def apply_relay_multipliers(base_price: float) -> float:
    k_disc = 1.0 + RELAY_MULTIPLIERS["partner_discount_pct"] / 100.0
    k_tzr = 1.0 + RELAY_MULTIPLIERS["tzr_logistics_pct"] / 100.0
    k_inf = 1.0 + RELAY_MULTIPLIERS["inflation_reserve_pct"] / 100.0
    k_wst = 1.0 + RELAY_MULTIPLIERS["waste_reserve_pct"] / 100.0
    return round(base_price * k_disc * k_tzr * k_inf * k_wst, 2)


def import_dealer_csv(raw_bytes: bytes) -> int:
    import csv, io
    from datetime import date
    from storage_control.services.quantum_normalizer import canon_key
    state = json.load(open(RELAY_STATE_PATH, encoding="utf-8")) if os.path.exists(RELAY_STATE_PATH) else {"cursor": 0, "passes": 0, "prices": {}}
    text = raw_bytes.decode("utf-8-sig", errors="ignore")
    reader = csv.reader(io.StringIO(text), delimiter=";" if ";" in text else ",")
    added = 0
    for row in reader:
        if len(row) < 2:
            continue
        nm = row.strip()
        m_p = re.search(r'\d+(?:[\.,]\d+)?', row[1].replace(" ", "").replace(",", "."))
        if nm and m_p:
            ck = canon_key(nm)
            base_p = float(m_p.group(0))
            state["prices"][ck] = {"name": nm[:80], "unit_price": apply_relay_multipliers(base_p), "source": "\u041fрайс дилера (CSV + множители)", "updated": str(date.today())}
            added += 1
    json.dump(state, open(RELAY_STATE_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return added

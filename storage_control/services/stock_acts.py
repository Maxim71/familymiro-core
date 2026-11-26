from datetime import datetime
from django.utils import timezone
from storage_control.models import StockMovement, PurchaseRequest, PhotoIntake, WarehouseItem


def register_stock_movement(
    *,
    movement_kind: str,
    material_name: str,
    qty: float,
    unit: str = "\u0448\u0442.",
    purchase_request_id: int | None = None,
    photo_intake_id: int | None = None,
    upd_batch_number: str = "",
    brigade_or_subcontractor: str = "",
    axes_and_ojr: str = "",
    responsible_itr: str = "\u0428\u0442\u0430\u0431 \u041f\u0422\u041e",
    doc_status: str = "CONFIRMED",
) -> tuple[StockMovement, list[str]]:
    alerts = []
    pr = PurchaseRequest.objects.filter(id=purchase_request_id).first() if purchase_request_id else None
    ph = PhotoIntake.objects.filter(id=photo_intake_id).first() if photo_intake_id else None
    if pr and not material_name:
        material_name = pr.material_name
        unit = pr.unit or unit
    if ph and not upd_batch_number:
        upd_batch_number = ph.doc_number or f"\u0424\u043e\u0442\u043e #{ph.id}"

    now_str = timezone.localtime(timezone.now()).strftime("%d.%m.%Y %H:%M")
    mv = StockMovement.objects.create(
        purchase_request=pr, photo_intake=ph, movement_kind=movement_kind, doc_status=doc_status,
        material_name=(material_name or "\u0422\u041c\u0426 \u043f\u043e \u0432\u0435\u0434\u043e\u043c\u043e\u0441\u0442\u0438")[:250],
        qty=round(float(qty or 0.0), 3), unit=(unit or "\u0448\u0442.")[:30],
        upd_batch_number=(upd_batch_number or "")[:115],
        brigade_or_subcontractor=(brigade_or_subcontractor or "\u0421\u0432\u043e\u044f \u0431\u0440\u0438\u0433\u0430\u0434\u0430")[:175],
        axes_and_ojr=(axes_and_ojr or f"\u041e\u0416\u0420 \u043e\u0442 {datetime.now():%d.%m.%Y}")[:155],
        responsible_itr=(responsible_itr or "\u0428\u0442\u0430\u0431 \u041f\u0422\u041e")[:115],
        history_log=[{"at": now_str, "status": doc_status, "by": responsible_itr}],
    )

    wh, _ = WarehouseItem.objects.get_or_create(material_name=mv.material_name, defaults={"unit": mv.unit, "stock_balance": 0.0})
    if doc_status == "CONFIRMED":
        if movement_kind in ("IN_UPD", "RET_M11"):
            wh.stock_balance = round(wh.stock_balance + mv.qty, 3)
        elif movement_kind in ("OUT_M11", "OUT_M15_SUB", "DEFECT_TORG2"):
            wh.stock_balance = round(max(0.0, wh.stock_balance - mv.qty), 3)
            if pr and pr.required_qty > 0 and wh.stock_balance < pr.required_qty * 0.15:
                alerts.append(f"\u0422\u041e\u0427\u041a\u0410 \u0417\u0410\u041a\u0410\u0417\u0410: \u043e\u0441\u0442\u0430\u0442\u043e\u043a \u00ab{mv.material_name}\u00bb ({wh.stock_balance} {mv.unit}) \u043d\u0438\u0436\u0435 15%!")
        wh.save(update_fields=["stock_balance"])

    if pr:
        if movement_kind in ("OUT_M11", "OUT_M15_SUB") and pr.status == "NEW":
            pr.status = "IN_PROGRESS"
            pr.brigade_assigned = mv.brigade_or_subcontractor
            pr.save(update_fields=["status", "brigade_assigned"])
        elif movement_kind == "WRITE_OFF_AOSR":
            pr.status = "CLOSED"
            pr.progress_pct = 100
            pr.save(update_fields=["status", "progress_pct"])

        issued = sum(m.qty for m in pr.movements.filter(movement_kind__in=["OUT_M11", "OUT_M15_SUB"], doc_status="CONFIRMED"))
        returned = sum(m.qty for m in pr.movements.filter(movement_kind="RET_M11", doc_status="CONFIRMED"))
        net_used = round(issued - returned, 3)
        limit_qty = round(pr.required_qty * 1.07, 3)
        if pr.required_qty > 0 and net_used > limit_qty:
            alerts.append(f"\u041f\u0415\u0420\u0415\u0420\u0410\u0421\u0425\u041e\u0414: \u043f\u043e \u00ab{mv.material_name}\u00bb \u0432\u044b\u0434\u0430\u043d\u043e {net_used} {mv.unit} \u043f\u0440\u0438 \u043b\u0438\u043c\u0438\u0442\u0435 {limit_qty} {mv.unit}!")

    return mv, alerts


def build_ks2_aosr_closing_summary() -> list[dict]:
    rows = []
    for pr in PurchaseRequest.objects.prefetch_related("movements").order_by("-id")[:25]:
        mvs = list(pr.movements.filter(doc_status="CONFIRMED"))
        if not mvs:
            continue
        issued = round(sum(m.qty for m in mvs if m.movement_kind in ("OUT_M11", "OUT_M15_SUB")) - sum(m.qty for m in mvs if m.movement_kind == "RET_M11"), 2)
        closed_aosr = round(sum(m.qty for m in mvs if m.movement_kind == "WRITE_OFF_AOSR"), 2)
        batches = ", ".join(sorted({m.upd_batch_number for m in mvs if m.upd_batch_number})) or "\u0411\u0435\u0437 \u0423\u041f\u0414"
        overrun = pr.required_qty > 0 and issued > round(pr.required_qty * 1.07, 2)
        rows.append({
            "pr_id": pr.id,
            "material": pr.material_name,
            "unit": pr.unit,
            "norm_qty": pr.required_qty,
            "issued_qty": issued,
            "closed_aosr_qty": closed_aosr,
            "batches": batches,
            "overrun": overrun,
            "status_label": "\u0413\u043e\u0442\u043e\u0432\u043e \u043a \u041a\u0421-2" if closed_aosr > 0 else "\u0412 \u043c\u043e\u043d\u0442\u0430\u0436\u0435 (\u0436\u0434\u0451\u0442 \u0410\u041e\u0421\u0420)",
        })
    return rows

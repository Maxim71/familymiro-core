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
        wh.save(update_fields=["stock_balance"])
    if pr and movement_kind in ("OUT_M11", "OUT_M15_SUB") and pr.status == "NEW":
        pr.status = "IN_PROGRESS"
        pr.brigade_assigned = mv.brigade_or_subcontractor
        pr.save(update_fields=["status", "brigade_assigned"])
    elif pr and movement_kind == "WRITE_OFF_AOSR":
        pr.status = "CLOSED"
        pr.progress_pct = 100
        pr.save(update_fields=["status", "progress_pct"])
    return mv, alerts

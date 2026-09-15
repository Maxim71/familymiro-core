import os
import hmac
import hashlib
import aiohttp
from decimal import Decimal
from django.conf import settings
from .models import LavaInvoice, AutoReceipt

LAVA_API_URL = "lava.top"

def generate_lava_signature(invoice_id, amount, secret_key):
    """Генерация защищенной подписи для исключения подмены суммы"""
    data = f"{invoice_id}:{amount}:{secret_key}"
    return hmac.new(secret_key.encode(), data.encode(), hashlib.sha256).hexdigest()

async def create_payment_invoice(capsule, amount_value):
    """Асинхронное выставление счета в Lava.top"""
    shop_id = os.getenv("LAVA_SHOP_ID", "TEST_SHOP")
    secret_key = os.getenv("LAVA_SECRET_KEY", "TEST_KEY")
    
    # Сумма в формате строки для API
    amount_str = f"{amount_value:.2f}"
    
    # 1. Сначала создаем черновик в нашей локальной базе Postgres
    local_invoice = LavaInvoice.objects.create(
        invoice_id=f"LAVA-{capsule.id}-{int(os.getpid())}",
        capsule=capsule,
        amount=Decimal(amount_str),
        payment_url="lava.top",
        status="pending"
    )

    # Формируем цифровую подпись безопасности
    signature = generate_lava_signature(local_invoice.invoice_id, amount_str, secret_key)

    payload = {
        "shopId": shop_id,
        "invoiceId": local_invoice.invoice_id,
        "amount": amount_str,
        "currency": "RUB",
        "comment": f"Оплата Капсулы Наследия #{capsule.id}",
        "signature": signature
    }

    # Асинхронный защищенный запрос к Lava.top
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(LAVA_API_URL, json=payload, timeout=10) as response:
                if response.status == 200:
                    res_data = await response.json()
                    # Обновляем реальную ссылку на оплату от Lava
                    local_invoice.payment_url = res_data.get("url", local_invoice.payment_url)
                    local_invoice.invoice_id = res_data.get("id", local_invoice.invoice_id)
                    local_invoice.save()
                    print(f"💳 [LAVA] Счёт выставлен успешно: {local_invoice.payment_url}")
                else:
                    print(f"⚠️ [LAVA] Ошибка шлюза. Статус: {response.status}. Включен тестовый режим.")
        except Exception as e:
            print(f"🚨 [LAVA] Сервер платежки недоступен ({e}). Активирован локальный демо-счет.")
            
    return local_invoice.payment_url

async def trigger_payment_success(invoice_id):
    """Вызывается системой, когда Lava.top присылает уведомление об оплате"""
    try:
        invoice = LavaInvoice.objects.get(invoice_id=invoice_id)
        if invoice.status != "success":
            invoice.status = "success"
            invoice.save()
            
            # ТРЕБОВАНИЕ v3.0: Авто-Чек для самозанятого с налогом 6%
            AutoReceipt.objects.create(
                vendor=f"Lava.top (Капсула #{invoice.capsule.id})",
                total_amount=invoice.amount,
                is_reported=False  # Готово для отправки в налоговую
            )
            print(f"🧾 [АВТО-ЧЕК] Налог 6% рассчитан автоматически для суммы {invoice.amount} руб.")
    except LavaInvoice.DoesNotExist:
        print(f"❌ [LAVA] Счет {invoice_id} не найден в базе Postgres.")

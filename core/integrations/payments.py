# core/integrations/payments.py
from typing import Any, Dict

import requests


def initiate_fawry_payment(
    amount: float,
    customer_name: str,
    phone: str,
    email: str,
    *,
    merchant_code: str = "YOUR_MERCHANT_CODE",
    signature: str = "GENERATED_SIGNATURE",
) -> Dict[str, Any]:
    """
    بدء عملية دفع عبر Fawry.

    Args:
        amount: قيمة المبلغ المطلوب دفعه.
        customer_name: اسم العميل.
        phone: رقم هاتف العميل.
        email: البريد الإلكتروني للعميل.
        merchant_code: كود التاجر من Fawry (يمكن تمريره أو ضبطه من الإعدادات).
        signature: التوقيع الرقمي المطلوب من Fawry (يجب توليده وفقًا للوثائق).

    Returns:
        dict: الاستجابة من بوابة Fawry (JSON).
    """
    payload: Dict[str, Any] = {
        "merchantCode": merchant_code,
        "customerName": customer_name,
        "customerMobile": phone,
        "customerEmail": email,
        "amount": amount,
        "paymentExpiry": 24,
        "chargeItems": [
            {
                "itemId": "001",
                "description": "فاتورة",
                "price": amount,
                "quantity": 1,
            }
        ],
        "signature": signature,
    }

    try:
        response = requests.post(
            "https://www.atfawry.com/ECommerceWeb/Fawry/payments",
            json=payload,
            timeout=20,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        return {"error": str(exc)}

    try:
        return response.json()
    except ValueError:
        return {"error": "Invalid JSON response"}

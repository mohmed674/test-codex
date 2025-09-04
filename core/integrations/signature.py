# core/integrations/signature.py
from typing import Any, Dict

import requests


def request_signature(pdf_url: str, client_email: str) -> Dict[str, Any]:
    """
    يرسل طلب توقيع إلكتروني إلى خدمة خارجية.

    Args:
        pdf_url: رابط الوثيقة PDF المطلوب توقيعها.
        client_email: البريد الإلكتروني للمستلم.

    Returns:
        dict: استجابة JSON من خدمة التوقيع.
    """
    payload = {
        "document": pdf_url,
        "recipient": client_email,
        "title": "توقيع عقد",
    }

    try:
        response = requests.post(
            "https://api.signature-service.com/send", json=payload, timeout=15
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        return {"error": str(exc)}

    try:
        return response.json()
    except ValueError:
        return {"error": "Invalid JSON response"}

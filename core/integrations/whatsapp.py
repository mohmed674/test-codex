# core/integrations/whatsapp.py
from typing import Any

try:
    from twilio.rest import Client  # type: ignore
except ImportError:
    Client = None  # fallback لو twilio مش موجودة


def send_whatsapp_message(
    to_number: str,
    message: str,
    *,
    account_sid: str | None = None,
    auth_token: str | None = None,
    from_number: str = "whatsapp:+14155238886",
) -> Any:
    """
    يرسل رسالة واتساب باستخدام Twilio.
    """
    if Client is None:
        raise RuntimeError("twilio package غير مثبت. قم بتشغيل: pip install twilio")

    sid = account_sid or "ACCOUNT_SID"
    token = auth_token or "AUTH_TOKEN"

    client = Client(sid, token)
    return client.messages.create(
        body=message,
        from_=from_number,
        to=f"whatsapp:{to_number}",
    )

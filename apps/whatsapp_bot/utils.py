# ERP_CORE/whatsapp_bot/utils.py

import requests
from django.conf import settings

def send_whatsapp_message(phone: str, message: str):
    """
    ✅ ترسل رسالة واتساب لأي رقم موظف
    - phone: رقم الهاتف بصيغة دولية (مثال: 2010xxxxxxx)
    - message: نص الرسالة
    """
    try:
        # 🔧 إعدادات الاتصال بواجهة واتساب بوت
        api_url = settings.WHATSAPP_API_URL
        api_token = settings.WHATSAPP_API_TOKEN

        payload = {
            "phone": phone,
            "message": message
        }

        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

        response = requests.post(api_url, json=payload, headers=headers)

        if response.status_code != 200:
            # ⚠️ في حالة فشل الإرسال
            print(f"[❌] فشل إرسال واتساب إلى {phone}: {response.text}")

    except Exception as e:
        print(f"[⚠️] خطأ أثناء إرسال رسالة واتساب: {e}")

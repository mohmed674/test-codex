# ERP_CORE/whatsapp_bot/ai_reply_engine.py

import re

MODEL_DB = {
    'M100': 'متوفر بسعر 200 جنيه.',
    'M200': 'متوفر بلونين بسعر 250 جنيه.',
    'M300': 'نفدت الكمية حاليًا.',
}

def generate_auto_reply(text):
    found_models = re.findall(r'M\d{3}', text.upper())
    if not found_models:
        return "يرجى إرسال أكواد الموديلات المطلوبة مثل: M100 أو M200."

    replies = []
    for code in found_models:
        status = MODEL_DB.get(code, "هذا الموديل غير موجود.")
        replies.append(f"موديل {code}: {status}")

    return "\n".join(replies)

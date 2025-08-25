import pyttsx3
from datetime import datetime

def trigger_voice_alert(message):
    """ينطق رسالة تنبيه صوتي باستخدام محرك النص إلى كلام"""
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 0.9)
    engine.say(message)
    engine.runAndWait()


def check_sales_anomalies(sale):
    """
    يراقب مبيعات غير منطقية أو إدخالات خاطئة في الفاتورة،
    ويرسل إنذارات صوتية حسب كل بند.
    """
    today = datetime.now().date()

    if sale.date > today:
        trigger_voice_alert(f"تحذير! تم إدخال تاريخ مبيعات في المستقبل للفاتورة رقم {sale.invoice_number}")

    # التحقق من كل بند في الفاتورة
    for item in sale.items.all():
        if item.quantity <= 0:
            trigger_voice_alert(f"تنبيه! البند {item.product.name} في الفاتورة {sale.invoice_number} بدون كمية.")
        if item.unit_price <= 0:
            trigger_voice_alert(f"تنبيه! سعر المنتج {item.product.name} في الفاتورة {sale.invoice_number} غير منطقي.")

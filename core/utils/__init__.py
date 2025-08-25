# D:\ERP_CORE\core\utils\__init__.py

from core.models import AccessLog

def log_user_action(user, action, ip_address=None, user_agent=None, location=None):
    AccessLog.objects.create(
        user=user,
        action=action,
        ip_address=ip_address,
        user_agent=user_agent,
        location=location
    )

# دالة تصدير PDF مؤقتة (dummy)
def render_to_pdf(template_src, context_dict):
    from django.http import HttpResponse
    return HttpResponse("PDF مؤقت (قم بتعديل الدالة لاحقًا)")

# دالة تصدير Excel مؤقتة (dummy)
def export_to_excel(queryset, filename='export.xlsx'):
    from django.http import HttpResponse
    return HttpResponse("Excel مؤقت (قم بتعديل الدالة لاحقًا)")


def get_entry_hint(field_name, section):
    # يمكنك تخصيص المنطق لاحقًا بناءً على اسم الحقل والقسم
    # الآن ترجع نص توضيحي بسيط أو فارغ لو مش معروف
    hints = {
        "name": "أدخل الاسم الكامل كما في الهوية.",
        "code": "كود فريد للعنصر أو الموظف.",
        "quantity": "أدخل الكمية المطلوبة أو المنتجة.",
    }
    # حاول تخصيص النص حسب القسم أيضًا إذا أردت
    return hints.get(field_name, "")

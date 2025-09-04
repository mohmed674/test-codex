# core/utils/__init__.py

from typing import Any, Mapping, Optional

from django.http import HttpResponse

from core.models import AccessLog


def log_user_action(
    user: Any,
    action: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    location: Optional[str] = None,
) -> None:
    """
    يسجل إجراء المستخدم في جدول AccessLog.
    """
    AccessLog.objects.create(
        user=user,
        action=action,
        ip_address=ip_address,
        user_agent=user_agent,
        location=location,
    )


def render_to_pdf(
    template_src: str, context_dict: Optional[Mapping[str, Any]] = None
) -> HttpResponse:
    """
    توليد PDF من قالب HTML (واجهة موحّدة).
    يستخدم WeasyPrint تحت الغطاء.
    """
    from core.utils.pdf_render import render_to_pdf_weasy

    return render_to_pdf_weasy(
        template_src, dict(context_dict or {}), filename="output.pdf"
    )


def export_to_excel(queryset: Any, filename: str = "export.xlsx") -> HttpResponse:
    """
    تصدير بيانات إلى ملف Excel (واجهة موحّدة).
    يمرر البيانات إلى أداة التصدير المتخصصة.
    """
    from core.utils.export_excel import export_to_excel as _export_to_excel

    return _export_to_excel(queryset, filename=filename)


def get_entry_hint(field_name: str, section: Optional[str]) -> str:
    """
    يرجع تلميحًا نصيًا مناسبًا للحقل/القسم.
    """
    hints: dict[str, str] = {
        "name": "أدخل الاسم الكامل كما في الهوية.",
        "code": "كود فريد للعنصر أو الموظف.",
        "quantity": "أدخل الكمية المطلوبة أو المنتجة.",
    }
    # يمكن لاحقًا تخصيص التلميح بالاعتماد على section
    return hints.get(field_name, "")

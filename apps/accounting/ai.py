# apps/accounting/ai.py
from contextlib import suppress

from django.apps import apps
from django.db import connection

from .models import JournalEntry


def _get_ai_model():
    """إرجاع موديل AIDecisionAlert فقط لو موجود والجدول متاح."""
    with suppress(Exception):
        model = apps.get_model("ai_decision", "AIDecisionAlert")
        table = model._meta.db_table  # type: ignore[attr-defined]
        if table in connection.introspection.table_names():
            return model
    return None


def detect_large_expense_entries(threshold: float = 50_000) -> None:
    """
    🔎 فحص قيود اليومية للعثور على قيود ذات مبالغ عالية.
    إنشاء تنبيه AI فقط لو كان التطبيق والجدول متاحين.
    """
    AIDecisionAlert = _get_ai_model()
    if AIDecisionAlert is None:
        return

    entries = JournalEntry.objects.filter(amount__gt=threshold)
    for entry in entries:
        with suppress(Exception):
            AIDecisionAlert.objects.create(
                section="accounting",
                alert_type="قيد محاسبي مرتفع",
                level="high",
                message=f"قيد محاسبي مرتفع بقيمة {entry.amount}: {entry.description}",
            )

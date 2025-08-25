from apps.ai_decision.models import AIDecisionAlert
from .models import JournalEntry

def detect_large_expense_entries():
    for entry in JournalEntry.objects.all():
        if entry.amount > 50000:
            AIDecisionAlert.objects.create(
                section='accounting',
                alert_type='قيد محاسبي مرتفع',
                level='high',
                message=f"قيد محاسبي مرتفع بقيمة {entry.amount}: {entry.description}"
            )

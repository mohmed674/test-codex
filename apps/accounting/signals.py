from contextlib import suppress

from django.apps import apps
from django.db import connection, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from apps.internal_monitoring.models import RiskIncident

from .models import (Account, AccountingSuggestionLog, Customer, JournalEntry,
                     JournalItem, ManufacturingOrder, Supplier)


# ====== أداة مساعدة: تنبيه AI آمن ومتوافق مع أي أسماء حقول ======
def ai_alert(section, alert_type, message, level="INFO"):
    """
    ينشئ سجل AIDecisionAlert فقط لو جدول الموديل موجود.
    - يكيّف أسماء الحقول حسب الموديل (title/description أو message/type...).
    - ينفّذ الإدراج بعد الـ commit لتجنّب كسر معاملة الأدمن.
    """
    with suppress(Exception):
        AIDecisionAlert = apps.get_model("ai_decision", "AIDecisionAlert")
    if "AIDecisionAlert" not in locals():
        return  # التطبيق/الموديل غير متوفر

    # ✅ اتأكد إن الجدول موجود قبل أي INSERT
    with suppress(Exception):
        table_name = AIDecisionAlert._meta.db_table
        if table_name not in connection.introspection.table_names():
            return

    # ✅ اجمع أسماء الحقول علشان نكيّف القيم
    with suppress(Exception):
        fields = {
            f.name for f in AIDecisionAlert._meta.get_fields() if hasattr(f, "attname")
        }
    if "fields" not in locals():
        return

    data = {}

    # section / category / module / area
    if "section" in fields:
        data["section"] = section
    elif "category" in fields:
        data["category"] = section
    elif "module" in fields:
        data["module"] = section
    elif "area" in fields:
        data["area"] = section

    # alert_type / type / event_type / code
    if "alert_type" in fields:
        data["alert_type"] = alert_type
    elif "type" in fields:
        data["type"] = alert_type
    elif "event_type" in fields:
        data["event_type"] = alert_type
    elif "code" in fields:
        data["code"] = alert_type

    # message / text / content / notes / description
    if "message" in fields:
        data["message"] = message
    elif "text" in fields:
        data["text"] = message
    elif "content" in fields:
        data["content"] = message
    elif "notes" in fields:
        data["notes"] = message
    elif "description" in fields:
        data["description"] = message

    # 🔎 دعم عناوين شائعة: title/subject/header
    if "title" in fields and "title" not in data:
        data["title"] = alert_type
    if "subject" in fields and "subject" not in data:
        data["subject"] = alert_type
    if "header" in fields and "header" not in data:
        data["header"] = alert_type
    if "description" in fields and "description" not in data:
        data["description"] = message

    # level / severity / priority / importance
    if "level" in fields:
        data["level"] = level
    elif "severity" in fields:
        data["severity"] = level
    elif "priority" in fields:
        data["priority"] = level
    elif "importance" in fields:
        data["importance"] = level

    # ✅ نفّذ الإدراج بعد الـ commit لتجنّب كسر المعاملة
    def _do_create():
        with suppress(Exception):
            AIDecisionAlert.objects.create(**data)

    with suppress(Exception):
        transaction.on_commit(_do_create)
        return
    _do_create()


def _name_of(obj):
    """يرجع اسم العميل/المورد بأذكى طريقة ممكنة."""
    if hasattr(obj, "name") and obj.name:
        return obj.name
    partner = getattr(obj, "partner", None)
    if partner and getattr(partner, "name", None):
        return partner.name
    return str(getattr(obj, "pk", ""))


# ✅ 1) تنبيه AI تلقائي عند إدخال قيد محاسبي كبير
@receiver(post_save, sender=JournalEntry)
def alert_ai_on_large_journal_entry(sender, instance, created, **kwargs):
    if not created:
        return
    amount = getattr(instance, "amount", None)
    if amount is None:
        debit = getattr(instance, "debit", 0) or 0
        credit = getattr(instance, "credit", 0) or 0
        amount = max(debit, credit)
    amount = amount or 0

    if amount >= 10000:
        ai_alert(
            section="Accounting",
            alert_type="قيد محاسبي كبير",
            message=(
                f"قيد محاسبي بمبلغ كبير: {amount} - "
                f"{getattr(instance, 'description', '')}"
            ),
            level="HIGH",
        )
        with suppress(Exception):
            RiskIncident.objects.create(
                user=getattr(instance, "created_by", None),
                category="Finance",
                event_type="قيد محاسبي بمبلغ ضخم",
                risk_level="HIGH",
                notes=(
                    f"مبلغ = {amount} / الوصف: "
                    f"{getattr(instance, 'description', '')}"
                ),
            )


# ✅ 2) تسجيل ذكي لأي قيد غير متوازن في السجل (مخاطر مالية)
@receiver(post_save, sender=JournalEntry)
def detect_unbalanced_entry(sender, instance, **kwargs):
    debit = getattr(instance, "debit", 0) or 0
    credit = getattr(instance, "credit", 0) or 0
    if abs(debit - credit) > 0.01:
        with suppress(Exception):
            AccountingSuggestionLog.objects.create(
                suggestion_type="إدخال غير متوازن",
                description=(
                    "تم إدخال قيد غير متوازن: "
                    f"مدين = {debit} / دائن = {credit} - "
                    f"({getattr(instance, 'description', '')})"
                ),
                risk_level="High",
                resolved=False,
            )
        with suppress(Exception):
            RiskIncident.objects.create(
                user=getattr(instance, "created_by", None),
                category="Finance",
                event_type="قيد محاسبي غير متوازن",
                risk_level="HIGH",
                notes=(
                    f"مدين: {debit} / دائن: {credit} / الوصف: "
                    f"{getattr(instance, 'description', '')}"
                ),
            )


# ✅ 3) قيد تلقائي ذكي عند تنفيذ أمر تصنيع ناجح
@receiver(post_save, sender=ManufacturingOrder)
def create_journal_entry_for_manufacturing(sender, instance, created, **kwargs):
    if created:
        return
    if getattr(instance, "status", "") != "completed":
        return
    # تفادي تكرار القيد
    if hasattr(instance, "journalentry_set") and instance.journalentry_set.exists():
        return

    total_cost = getattr(instance, "total_cost", 0) or 0
    if total_cost <= 0:
        return

    expense_account = Account.objects.filter(type="expense").first()
    inventory_account = Account.objects.filter(type="asset").first()
    if not (expense_account and inventory_account):
        return

    # تحديد الحقول المتاحة في JournalEntry
    with suppress(Exception):
        je_fields = {
            f.name for f in JournalEntry._meta.get_fields() if hasattr(f, "attname")
        }
    if "je_fields" not in locals():
        je_fields = set()

    entry_kwargs = {}
    candidates = {
        "date": timezone.localdate(),
        "description": (
            "تكلفة تصنيع المنتج "
            f"{getattr(getattr(instance, 'bom', None), 'product_name', '')}"
        ),
        "amount": total_cost,
        "debit": total_cost,
        "credit": total_cost,
        "created_by": None,
        "entry_type": "system",
    }
    for k, v in candidates.items():
        if k in je_fields:
            entry_kwargs[k] = v

    entry = JournalEntry.objects.create(**entry_kwargs)

    # قيود تفصيلية
    with suppress(Exception):
        JournalItem.objects.create(
            entry=entry,
            account=expense_account,
            debit=total_cost,
            credit=0,
        )
        JournalItem.objects.create(
            entry=entry,
            account=inventory_account,
            debit=0,
            credit=total_cost,
        )


# ✅ 4) تنبيه عند تسجيل حساب مالي جديد مرتبط بعميل أو مورد
@receiver(post_save, sender=Account)
def alert_ai_on_new_account_linked(sender, instance, created, **kwargs):
    if not created:
        return
    if getattr(instance, "customer", None):
        ai_alert(
            section="Accounting",
            alert_type="ربط حساب بعميل",
            message=(
                "تم إنشاء حساب مالي مرتبط بالعميل: " f"{_name_of(instance.customer)}"
            ),
            level="MEDIUM",
        )
    elif getattr(instance, "supplier", None):
        ai_alert(
            section="Accounting",
            alert_type="ربط حساب بمورد",
            message=(
                "تم إنشاء حساب مالي مرتبط بالمورد: " f"{_name_of(instance.supplier)}"
            ),
            level="MEDIUM",
        )


# ✅ 5) تنبيه ذكي إذا تم إنشاء مورد أو عميل جديد
@receiver(post_save, sender=Supplier)
@receiver(post_save, sender=Customer)
def alert_on_new_partner(sender, instance, created, **kwargs):
    if not created:
        return
    partner_type = "مورد" if isinstance(instance, Supplier) else "عميل"
    ai_alert(
        section="Accounting",
        alert_type=f"إضافة {partner_type} جديد",
        message=f"تم إضافة {partner_type} جديد: {_name_of(instance)}",
        level="INFO",
    )

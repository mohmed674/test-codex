from django.db import transaction
from apps.accounting.models import JournalEntry, JournalItem
from apps.inventory.models import InventoryTransaction
from apps.payroll.models import WorkRecord
from apps.evaluation.models import Evaluation
from apps.ai_decision.models import AIDecisionLog
from datetime import datetime
from decimal import Decimal

# ✅ 1. سحب خامات من المخزن لأمر تشغيل
def auto_consume_materials(work_order):
    from apps.products.models import ProductMaterial
    materials = ProductMaterial.objects.filter(product=work_order.product)

    for mat in materials:
        total_qty = mat.quantity_per_unit * work_order.quantity

        InventoryTransaction.objects.create(
            product=mat.material,
            quantity=total_qty,
            transaction_type='out',
            source='WorkOrder',
            source_id=work_order.id,
            description=f'سحب خامة ({mat.material}) لأمر تشغيل رقم {work_order.code}',
            branch=work_order.branch
        )


# ✅ 2. تسجيل التكلفة تلقائيًا في الحسابات
def auto_record_cost(work_order, total_cost):
    with transaction.atomic():
        entry = JournalEntry.objects.create(
            date=work_order.start_date or datetime.today(),
            description=f'قيد تكلفة أمر تشغيل رقم {work_order.code}',
            source_model='WorkOrder',
            source_id=work_order.id
        )

        JournalItem.objects.create(
            entry=entry,
            account='مصروفات إنتاج',
            debit=total_cost,
            credit=Decimal('0.00')
        )

        JournalItem.objects.create(
            entry=entry,
            account='المخزون – خامات',
            debit=Decimal('0.00'),
            credit=total_cost
        )


# ✅ 3. تسجيل العمل للعامل تلقائيًا
def auto_record_work(employee, quantity, work_order):
    WorkRecord.objects.create(
        employee=employee,
        quantity=quantity,
        work_order=work_order,
        date=datetime.today()
    )


# ✅ 4. تحديث تقييم الموظف حسب الأداء
def auto_update_evaluation(employee, delta_score, reason='مشاركة في الإنتاج'):
    Evaluation.objects.create(
        employee=employee,
        score_change=delta_score,
        reason=reason,
        date=datetime.today()
    )


# ✅ 5. إرسال تنبيه لنظام الذكاء الاصطناعي
def auto_notify_ai(category, message, source, source_id):
    AIDecisionLog.objects.create(
        category=category,
        message=message,
        related_model=source,
        related_id=source_id,
        created_at=datetime.now()
    )

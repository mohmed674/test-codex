from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ProductionOrder, MaterialConsumption
from apps.inventory.models import InventoryTransaction
from apps.accounting.models import JournalEntry
from apps.payroll.models import PieceRateRecord
from apps.evaluation.models import Evaluation
from apps.maintenance.models import MachineUsageLog
from apps.ai_decision.models import DecisionLog
from decimal import Decimal
from django.utils import timezone


@receiver(post_save, sender=ProductionOrder)
def handle_production_order_created(sender, instance, created, **kwargs):
    if not created:
        return

    # ✅ 1. سحب خامات من المخزون + تسجيل استهلاك
    raw_materials = instance.required_materials.all() if hasattr(instance, 'required_materials') else []
    for material in raw_materials:
        InventoryTransaction.objects.create(
            item=material.item,
            quantity=-material.quantity_required,
            transaction_type='OUT',
            related_order=instance,
            note=f"سحب خامة لأمر إنتاج {instance.order_number}"
        )
        MaterialConsumption.objects.create(
            order=instance,
            material_name=material.item.name,
            quantity_used=material.quantity_required,
            unit=material.item.unit
        )

    # ✅ 2. تسجيل قيد تكلفة الخامات في المحاسبة
    total_cost = sum([
        (m.item.unit_cost or 0) * Decimal(m.quantity_required or 0)
        for m in raw_materials
    ])
    if total_cost > 0:
        JournalEntry.objects.create(
            description=f"تكلفة خامات أمر إنتاج {instance.order_number}",
            debit_account="تكلفة إنتاج",
            credit_account="المخزون",
            amount=total_cost,
            entry_date=timezone.now()
        )

    # ✅ 3. تسجيل المرتب بنظام القطعة للموظفين المشاركين
    if instance.assigned_to.exists():
        for employee in instance.assigned_to.all():
            PieceRateRecord.objects.create(
                employee=employee,
                production_order=instance,
                pieces_count=0,
                rate_per_piece=getattr(employee.job_title, 'default_piece_rate', 0),
                date=timezone.now()
            )

            # ✅ 4. تقييم الأداء والانضباط تلقائيًا
            Evaluation.objects.create(
                employee=employee,
                score=5,
                note=f"مشاركة في أمر إنتاج {instance.order_number}",
                evaluation_date=timezone.now()
            )

    # ✅ 5. تسجيل استهلاك الماكينات تلقائيًا
    if hasattr(instance, 'used_machines'):
        for machine in instance.used_machines.all():
            MachineUsageLog.objects.create(
                machine=machine,
                production_order=instance,
                usage_hours=instance.estimated_hours or 0,
                usage_date=timezone.now()
            )

    # ✅ 6. تسجيل في نظام الذكاء الاصطناعي للمراجعة
    DecisionLog.objects.create(
        related_module="الإنتاج",
        description=f"تم إصدار أمر إنتاج رقم {instance.order_number}",
        created_at=timezone.now(),
        status="pending_analysis"
    )

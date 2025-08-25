# ERP_CORE/discipline/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DisciplineRecord
from apps.ai_decision.models import AIDecisionAlert
from apps.internal_monitoring.models import RiskIncident  # ✅ نظام المراقبة
from apps.whatsapp_bot.utils import send_whatsapp_message  # ✅ دالة إرسال واتساب

@receiver(post_save, sender=DisciplineRecord)
def notify_ai_on_disciplinary_action(sender, instance, created, **kwargs):
    if created:
        employee_name = instance.employee.name
        employee_phone = instance.employee.phone  # يفترض أن رقم الهاتف موجود في نموذج الموظف
        action_type = instance.type
        reason = instance.reason or "بدون توضيح"
        
        # ✅ تنبيه الذكاء الاصطناعي
        AIDecisionAlert.objects.create(
            section='discipline',
            alert_type='إجراء تأديبي',
            message=f"📌 إجراء تأديبي جديد: {action_type} للموظف {employee_name}",
            level='warning'
        )

        # ✅ تسجيل مخالفة في النظام الذكي للمراقبة
        RiskIncident.objects.create(
            user=None,  # يمكن ربطه بـ request.user لاحقًا إذا توفرت المعلومة
            category="HR",
            event_type="إجراء تأديبي جديد",
            risk_level="MEDIUM" if action_type != 'إنذار' else "LOW",
            notes=f"📝 تم تسجيل {action_type} على {employee_name}: {reason}"
        )

        # ✅ إرسال رسالة واتساب تلقائية للموظف
        if employee_phone:
            if action_type == "إنذار":
                msg = f"🔴 {employee_name}، تم إصدار إنذار رسمي ضدك بسبب: {reason}. نرجو الالتزام بقواعد المصنع."
            elif action_type == "خصم":
                msg = f"📉 {employee_name}، تم تطبيق خصم على راتبك بسبب: {reason}."
            else:
                msg = f"⚠️ {employee_name}، تم تسجيل {action_type} ضدك بسبب: {reason}."

            send_whatsapp_message(phone=employee_phone, message=msg)

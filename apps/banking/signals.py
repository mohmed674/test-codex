# apps/banking/signals.py
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=get_user_model())
def create_employee_for_new_user(sender, instance, created, **kwargs):
    """
    عند إنشاء مستخدم جديد: حاول أن تنشئ Employee فقط إذا كان الموديل يدعم الحقول المتوقعة.
    لا تُسقط إنشاء المستخدم في حال عدم تطابق الحقول.
    """
    if not created:
        return

    try:
        from apps.employees.models import Employee
    except Exception:
        # موديل employees غير متاح؟
        return

    try:
        field_names = {f.name for f in Employee._meta.get_fields()}
        payload = {}

        # لو في حقل user في Employee استخدمه
        if "user" in field_names:
            payload["user"] = instance

        # لو في حقل full_name في Employee املأه من اسم المستخدم
        if "full_name" in field_names:
            full_name = (
                getattr(instance, "get_full_name", lambda: "")()
                or getattr(instance, "username", "")
                or getattr(instance, "email", "")
            )
            payload["full_name"] = full_name

        # لو مفيش أي حقول متاحة، انسحب بهدوء
        if not payload:
            return

        # تجنب التكرار لو فيه علاقة OneToOne
        if "user" in payload:
            Employee.objects.get_or_create(
                user=payload["user"],
                defaults={k: v for k, v in payload.items() if k != "user"},
            )
        else:
            Employee.objects.create(**payload)

    except Exception:
        # لا تكسر إنشاء المستخدم بسبب أي خطأ في السيجنال
        return

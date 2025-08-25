from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from apps.employees.models import Employee


@receiver(post_save, sender=User)
def create_employee_for_new_user(sender, instance, created, **kwargs):
    """
    يتم تلقائيًا إنشاء سجل موظف مرتبط عند إنشاء مستخدم جديد،
    فقط في حال عدم وجود موظف مرتبط مسبقًا.
    """
    if created and not hasattr(instance, 'employee'):
        Employee.objects.create(
            user=instance,
            full_name=instance.get_full_name() or instance.username
        )

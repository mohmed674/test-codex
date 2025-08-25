from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ProductVersion, ChangeRequest


@receiver(post_save, sender=ProductVersion)
def activate_new_version(sender, instance, created, **kwargs):
    """
    عند إنشاء نسخة جديدة من المنتج يتم تعطيل النسخ القديمة
    وتفعيل النسخة الجديدة بشكل تلقائي
    """
    if created and instance.is_active:
        ProductVersion.objects.filter(
            product=instance.product
        ).exclude(id=instance.id).update(is_active=False)


@receiver(post_save, sender=ChangeRequest)
def update_change_request_status(sender, instance, created, **kwargs):
    """
    تحديث حالة طلب التغيير:
    لو فيه نسخة مستهدفة (to_version) يتم تفعيلها مباشرة بعد الموافقة والتنفيذ
    """
    if instance.status == "implemented" and instance.to_version:
        # تفعيل النسخة الجديدة
        instance.to_version.is_active = True
        instance.to_version.save()
        # تعطيل النسخة القديمة إن وجدت
        if instance.from_version:
            instance.from_version.is_active = False
            instance.from_version.save()

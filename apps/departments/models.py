# ERP_CORE/departments/models.py
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.core.exceptions import ValidationError

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="اسم القسم")
    description = models.TextField(blank=True, null=True, verbose_name="وصف القسم")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    slug = models.SlugField(max_length=120, unique=True, blank=True, null=True, verbose_name="رابط مخصص")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="تاريخ الإنشاء")  # تم تعديل الحقل
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تعديل")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # توليد رابط مخصص تلقائيًا إن لم يتم إدخاله يدويًا
        if not self.slug and self.name:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def clean(self):
        # تحقق ذكي من الطول والبيانات
        if len(self.name.strip()) < 2:
            raise ValidationError({'name': "❌ اسم القسم قصير جدًا، يجب أن لا يقل عن حرفين."})
        if Department.objects.exclude(pk=self.pk).filter(slug=self.slug).exists():
            raise ValidationError({'slug': "⚠️ هذا الرابط مستخدم من قبل قسم آخر."})

    class Meta:
        ordering = ['name']
        verbose_name = "قسم"
        verbose_name_plural = "الأقسام"

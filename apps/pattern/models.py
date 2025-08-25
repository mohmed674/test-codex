from django.db import models
from apps.production.models import ProductionOrder
from django.utils.translation import gettext_lazy as _

class PatternType(models.TextChoices):
    BASIC = 'basic', _('أساسي')
    PRINT = 'print', _('طباعة')
    EMBROIDERY = 'embroidery', _('تطريز')
    LASER_CUT = 'laser', _('قص ليزر')


class PatternDesign(models.Model):
    name = models.CharField(max_length=200, verbose_name="اسم التصميم")
    description = models.TextField(blank=True, null=True, verbose_name="الوصف")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to="patterns/images/", blank=True, null=True, verbose_name="صورة")
    gerber_file = models.FileField(upload_to="patterns/gerber/", blank=True, null=True, verbose_name="ملف Gerber")
    pattern_type = models.CharField(max_length=20, choices=PatternType.choices, default=PatternType.BASIC)

    def __str__(self):
        return self.name


class PatternPiece(models.Model):
    design = models.ForeignKey(PatternDesign, on_delete=models.CASCADE, related_name="pieces")
    name = models.CharField(max_length=100, verbose_name="اسم القطعة")
    fabric_type = models.CharField(max_length=100, verbose_name="نوع القماش")
    length_cm = models.FloatField(verbose_name="الطول (سم)")
    width_cm = models.FloatField(verbose_name="العرض (سم)")
    quantity = models.PositiveIntegerField(verbose_name="الكمية")

    def __str__(self):
        return f"{self.name} - {self.design.name}"


class PatternExecution(models.Model):
    production_order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, related_name="executed_patterns")
    design = models.ForeignKey(PatternDesign, on_delete=models.CASCADE)
    executed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    operator_name = models.CharField(max_length=100, verbose_name="اسم منفذ الباترون")

    def __str__(self):
        return f"تنفيذ {self.design.name} لأمر {self.production_order.order_number}"

from django.db import models
from apps.employees.models import Employee
from django.contrib.auth.models import User

class AIDecisionAlert(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class DecisionAnalysis(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='decisions')
    decision_type = models.CharField(max_length=100)
    production_score = models.FloatField()
    behavior_score = models.FloatField()
    financial_impact = models.FloatField()
    final_suggestion = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} - {self.decision_type}"


# ✅ كلاس سجل قرارات الذكاء الاصطناعي
class AIDecisionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="المستخدم")
    event_type = models.CharField(max_length=100, verbose_name="نوع الحدث")
    description = models.TextField(verbose_name="الوصف")
    risk_level = models.CharField(
        max_length=20,
        choices=[
            ('Low', 'منخفض'),
            ('Medium', 'متوسط'),
            ('High', 'مرتفع'),
        ],
        default='Medium',
        verbose_name="درجة الخطورة"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    def __str__(self):
        return f"{self.user} - {self.event_type} ({self.risk_level})"

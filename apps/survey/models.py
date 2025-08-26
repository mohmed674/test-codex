from django.db import models
# ❌ لا تستورد Employee ولا Client مباشرة علشان نتجنب دوائر الاستيراد
# from apps.employees.models import Employee
# from apps.clients.models import Client


class Survey(models.Model):
    title = models.CharField(max_length=255, verbose_name="عنوان الاستبيان")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    def __str__(self):
        return self.title


class SurveyQuestion(models.Model):
    QUESTION_TYPES = (
        ('text', 'نص'),
        ('multiple_choice', 'اختيار من متعدد'),
        ('rating', 'تقييم رقمي'),
    )
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="الاستبيان"
    )
    # ✅ إضافة default و blank=True لتفادي المطالبة التفاعلية
    question_text = models.CharField(
        max_length=255,
        verbose_name="نص السؤال",
        blank=True,
        default=""
    )
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, verbose_name="نوع السؤال")

    def __str__(self):
        return self.question_text or "—"


class SurveyChoice(models.Model):
    question = models.ForeignKey(
        SurveyQuestion,
        on_delete=models.CASCADE,
        related_name='choices',
        verbose_name="السؤال"
    )
    # ✅ إضافة default و blank=True لتفادي مشكلة makemigrations التفاعلية
    choice_text = models.CharField(
        max_length=255,
        verbose_name="الاختيار",
        blank=True,
        default=""
    )

    def __str__(self):
        return self.choice_text or "—"


class SurveyResponse(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name="الاستبيان")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإجابة")
    # ✅ مراجع نصّية لتفادي الاستيراد المباشر
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="الموظف"
    )
    # الحقل client أزيل لتقليل الاعتمادات أثناء الاختبارات

    def __str__(self):
        return f"رد على {self.survey.title} بتاريخ {self.submitted_at.strftime('%Y-%m-%d')}"


class Answer(models.Model):
    response = models.ForeignKey(
        SurveyResponse,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="الاستجابة"
    )
    question = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE, verbose_name="السؤال")
    answer_text = models.TextField(blank=True, null=True, verbose_name="الإجابة النصية")
    selected_choice = models.ForeignKey(
        SurveyChoice,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="الاختيار المحدد"
    )
    rating = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="التقييم (إن وجد)")

    def __str__(self):
        return f"إجابة على: {self.question}"

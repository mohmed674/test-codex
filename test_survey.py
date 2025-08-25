import pytest
from django.apps import apps
from django.db import connection


@pytest.mark.django_db
def test_survey_tables_exist_after_migrate():
    """
    يتحقق من وجود الجداول الأساسية الخاصة بتطبيق survey
    والتأكد أن الترحيلات طبّقت بشكل صحيح.
    """
    existing = set(connection.introspection.table_names())
    expected = {
        "survey_survey",       # جدول الاستبيانات
        "survey_question",     # جدول الأسئلة
        "survey_answer",       # جدول الإجابات
    }
    missing = [t for t in expected if t not in existing]
    assert not missing, f"Survey tables missing: {missing}"


def test_survey_app_is_installed():
    """
    التأكد أن تطبيق survey مسجّل ضمن INSTALLED_APPS.
    """
    installed = {cfg.name for cfg in apps.get_app_configs()}
    assert "survey" in installed, "survey app is not installed"


@pytest.mark.django_db
def test_create_basic_survey_objects():
    """
    تجربة إنشاء survey بسيط مع سؤال وإجابة،
    للتحقق من أن الـ ORM يعمل بدون مشاكل.
    """
    Survey = apps.get_model("survey", "Survey")
    Question = apps.get_model("survey", "Question")
    Answer = apps.get_model("survey", "Answer")

    survey = Survey.objects.create(title="Test Survey")
    q1 = Question.objects.create(survey=survey, text="هل النظام يعمل؟")
    Answer.objects.create(question=q1, text="نعم")
    Answer.objects.create(question=q1, text="لا")

    assert Survey.objects.count() == 1
    assert Question.objects.count() == 1
    assert Answer.objects.count() == 2

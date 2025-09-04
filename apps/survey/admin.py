# apps/survey/admin.py
from contextlib import suppress

from django.contrib import admin

from apps.survey.models import (Answer, Survey, SurveyChoice, SurveyQuestion,
                                SurveyResponse)

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Survey)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(SurveyQuestion)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(SurveyChoice)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(SurveyResponse)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Answer)

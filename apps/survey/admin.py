from django.contrib import admin
from apps.survey.models import *

# ✅ Auto-registered models
try:
    admin.site.register(Survey)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(SurveyQuestion)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(SurveyChoice)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(SurveyResponse)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(Answer)
except admin.sites.AlreadyRegistered:
    pass
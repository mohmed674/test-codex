from django.contrib import admin
from apps.evaluation.models import *

# ✅ Auto-registered models
try:
    admin.site.register(Evaluation)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(LatenessAbsence)
except admin.sites.AlreadyRegistered:
    pass
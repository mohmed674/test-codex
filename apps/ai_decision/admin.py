from django.contrib import admin
from apps.ai_decision.models import *

# ✅ Auto-registered models
try:
    admin.site.register(AIDecisionAlert)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(DecisionAnalysis)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(AIDecisionLog)
except admin.sites.AlreadyRegistered:
    pass
from django.contrib import admin
from apps.knowledge_center.models import *

# ✅ Auto-registered models
try:
    admin.site.register(Category)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(Article)
except admin.sites.AlreadyRegistered:
    pass
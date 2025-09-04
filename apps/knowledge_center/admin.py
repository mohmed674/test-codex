from contextlib import suppress

from django.contrib import admin

from apps.knowledge_center.models import Article, Category

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Category)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Article)

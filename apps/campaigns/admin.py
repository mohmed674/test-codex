from django.contrib import admin
from .models import Campaign, CampaignTarget

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'channel', 'scheduled_date', 'created_by', 'is_sent')
    list_filter = ('channel', 'is_sent')
    search_fields = ('name', 'content', 'created_by__full_name')
    date_hierarchy = 'scheduled_date'
    ordering = ('-scheduled_date',)

@admin.register(CampaignTarget)
class CampaignTargetAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'client', 'is_delivered')
    list_filter = ('is_delivered',)
    search_fields = ('campaign__name', 'client__name')

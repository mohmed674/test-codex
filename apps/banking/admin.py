# apps/banking/admin.py — Final, professional registration (Sprint 3 / Banking)

from django.contrib import admin
from .models import (
    BankProvider,
    BankAccount,
    Payment,
    Transfer,
    BankTransaction,
    ReconciliationBatch,
    WebhookEvent,
)


@admin.register(BankProvider)
class BankProviderAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "base_url", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "code", "base_url")
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ("name", "provider", "account_number", "currency", "is_default", "updated_at")
    list_filter = ("provider", "currency", "is_default")
    search_fields = ("name", "account_number", "provider__name", "provider__code")
    ordering = ("provider", "name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("reference", "provider", "account", "direction", "method", "status", "amount", "currency", "created_at")
    list_filter = ("status", "direction", "method", "currency", "provider")
    search_fields = ("reference", "account__name", "provider__name", "provider__code", "external_id")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ("reference", "provider", "source_account", "destination_account", "status", "amount", "currency", "scheduled_at", "executed_at")
    list_filter = ("status", "currency", "provider")
    search_fields = ("reference", "source_account__name", "destination_account__name", "provider__code")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")


@admin.register(BankTransaction)
class BankTransactionAdmin(admin.ModelAdmin):
    list_display = ("account", "type", "amount", "currency", "booked_at", "value_date", "external_id", "balance_after")
    list_filter = ("type", "currency", "account")
    search_fields = ("account__name", "description", "external_id")
    ordering = ("-booked_at",)
    date_hierarchy = "booked_at"


@admin.register(ReconciliationBatch)
class ReconciliationBatchAdmin(admin.ModelAdmin):
    list_display = ("account", "provider", "status", "period_start", "period_end", "matched_count", "unmatched_count")
    list_filter = ("status", "provider")
    search_fields = ("account__name", "provider__code", "notes")
    ordering = ("-created_at",)
    date_hierarchy = "period_start"
    readonly_fields = ("created_at", "updated_at")


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ("provider", "event_type", "status", "received_at", "processed_at")
    list_filter = ("status", "provider", "event_type")
    search_fields = ("provider__code", "event_type", "signature")
    ordering = ("-received_at",)
    date_hierarchy = "received_at"

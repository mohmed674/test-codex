# apps/inventory/admin.py — Admin registration completed (Sprint 1 / Admin P1)

from django.contrib import admin
from apps.inventory.models import (
    RawMaterial,
    Warehouse,
    InventoryItem,
    InventoryMovement,
    InventoryAudit,
    InventoryAuditItem,
    InventoryDiscrepancyInvestigation,
    Inventory,  # Proxy to InventoryItem
)

# ── Admin classes (professional, production-ready) ─────────────────────────────

@admin.register(RawMaterial)
class RawMaterialAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "unit")
    search_fields = ("code", "name")
    list_filter = ("unit",)
    ordering = ("code",)


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "manager")
    search_fields = ("name", "location", "manager")
    ordering = ("name",)


class _BaseInventoryItemAdmin(admin.ModelAdmin):
    list_display = ("product", "warehouse", "quantity", "unit", "min_threshold", "last_updated")
    list_filter = ("warehouse", "unit")
    search_fields = ("product__name", "warehouse__name")
    ordering = ("-last_updated",)
    readonly_fields = ("last_updated",)


@admin.register(InventoryItem)
class InventoryItemAdmin(_BaseInventoryItemAdmin):
    pass


@admin.register(Inventory)  # Proxy model visible in Admin as a clean alias
class InventoryAdmin(_BaseInventoryItemAdmin):
    pass


@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = ("item", "movement_type", "quantity", "date")
    list_filter = ("movement_type", "date")
    search_fields = ("item__product__name", "item__warehouse__name")
    ordering = ("-date",)


@admin.register(InventoryAudit)
class InventoryAuditAdmin(admin.ModelAdmin):
    list_display = ("audit_type", "performed_by", "performed_at")
    list_filter = ("audit_type", "performed_at")
    search_fields = ("performed_by__username",)
    ordering = ("-performed_at",)


@admin.register(InventoryAuditItem)
class InventoryAuditItemAdmin(admin.ModelAdmin):
    list_display = ("audit", "product", "system_quantity", "physical_quantity", "difference")
    list_filter = ("audit__audit_type",)
    search_fields = ("audit__performed_by__username", "product__name")
    ordering = ("audit", "product")


@admin.register(InventoryDiscrepancyInvestigation)
class InventoryDiscrepancyInvestigationAdmin(admin.ModelAdmin):
    list_display = ("audit_item", "is_resolved", "reported_to", "created_at")
    list_filter = ("is_resolved", "created_at")
    search_fields = ("audit_item__product__name", "reported_to__username")
    ordering = ("-created_at",)

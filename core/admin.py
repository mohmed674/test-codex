from django.contrib import admin
from .models import (
    JobTitle, Unit, EvaluationCriteria,
    ProductionStageType, RiskThreshold,
    DepartmentRole, Role, RoleRequest,
    AccessLog, PermissionMatrix, TemporaryAccessOverride,
    Department, Employee, Client, SmartAccountTemplate
)

@admin.register(JobTitle)
class JobTitleAdmin(admin.ModelAdmin):
    list_display = ['name', 'salary_type', 'default_piece_rate', 'hourly_rate', 'is_active']
    search_fields = ['name']
    list_filter = ['salary_type', 'is_active']

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'unit_type', 'is_active', 'is_bulk_unit']
    search_fields = ['name', 'abbreviation']
    list_filter = ['unit_type', 'is_bulk_unit', 'is_active']

@admin.register(EvaluationCriteria)
class EvaluationCriteriaAdmin(admin.ModelAdmin):
    list_display = ['name', 'weight', 'criteria_type', 'is_active']
    search_fields = ['name']
    list_filter = ['criteria_type', 'is_active']

@admin.register(ProductionStageType)
class ProductionStageTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'estimated_duration_minutes', 'requires_machine', 'is_active']
    search_fields = ['name']
    list_filter = ['requires_machine', 'is_active']

@admin.register(RiskThreshold)
class RiskThresholdAdmin(admin.ModelAdmin):
    list_display = ['risk_type', 'threshold_value', 'severity_level', 'applies_to_section', 'is_active']
    list_filter = ['severity_level', 'is_active']
    search_fields = ['risk_type', 'applies_to_section']

@admin.register(DepartmentRole)
class DepartmentRoleAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_by', 'created_at']
    search_fields = ['name']
    list_filter = ['is_active']

@admin.register(RoleRequest)
class RoleRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'requested_role', 'status', 'requested_at', 'reviewed_by']
    list_filter = ['status']
    search_fields = ['user__username', 'requested_role__name']

@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'timestamp', 'ip_address', 'location']
    search_fields = ['user__username', 'action', 'ip_address', 'location']
    list_filter = ['timestamp']

@admin.register(PermissionMatrix)
class PermissionMatrixAdmin(admin.ModelAdmin):
    list_display = ['role', 'model_name', 'can_create', 'can_read', 'can_update', 'can_delete']
    list_filter = ['can_create', 'can_read', 'can_update', 'can_delete']
    search_fields = ['model_name', 'role__name']

@admin.register(TemporaryAccessOverride)
class TemporaryAccessOverrideAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'granted_by', 'granted_at', 'expires_at', 'is_revoked']
    search_fields = ['user__username', 'role__name']
    list_filter = ['is_revoked', 'is_auto_generated']

# تسجيل النماذج الناقصة بدون تخصيص
admin.site.register(Department)
admin.site.register(Employee)
admin.site.register(Client)
admin.site.register(SmartAccountTemplate)

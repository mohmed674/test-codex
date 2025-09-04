from contextlib import suppress

from django.contrib import admin

from apps.qms.models import (AQLCodeLetter, AQLPlan, AQLSamplingRow,
                             CAPAAction, CapabilityStudy, CAPARecord,
                             ControlChart, ControlProcess, DataPoint,
                             DefectType, InspectionLot, InspectionResult,
                             Nonconformity, QualityCharacteristic, Subgroup)

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(QualityCharacteristic)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(DefectType)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(AQLPlan)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(AQLCodeLetter)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(AQLSamplingRow)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(InspectionLot)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(InspectionResult)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Nonconformity)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(ControlProcess)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(ControlChart)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Subgroup)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(DataPoint)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(CapabilityStudy)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(CAPARecord)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(CAPAAction)

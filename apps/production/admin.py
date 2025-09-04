from contextlib import suppress

from django.contrib import admin

from apps.production.models import (BillOfMaterials, FinalProductOutput,
                                    MaterialConsumption, ProductionLog,
                                    ProductionOrder, ProductionScanQR,
                                    ProductionStage, ProductVersion,
                                    QualityCheck)

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(ProductionOrder)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(ProductionStage)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(MaterialConsumption)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(FinalProductOutput)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(ProductionScanQR)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(BillOfMaterials)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(QualityCheck)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(ProductVersion)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(ProductionLog)

from django.contrib import admin
from apps.qms.models import *

# ✅ Auto-registered models
try:
    admin.site.register(QualityCharacteristic)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(DefectType)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(AQLPlan)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(AQLCodeLetter)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(AQLSamplingRow)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(InspectionLot)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(InspectionResult)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(Nonconformity)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(ControlProcess)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(ControlChart)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(Subgroup)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(DataPoint)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(CapabilityStudy)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(CAPARecord)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(CAPAAction)
except admin.sites.AlreadyRegistered:
    pass
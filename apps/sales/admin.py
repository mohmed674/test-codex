from django.contrib import admin
from apps.sales.models import *

# ✅ Auto-registered models
try:
    admin.site.register(SaleInvoice)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(SaleItem)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(ClientPointsLog)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(SalesPerformance)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(ProductSalesAnalysis)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(ClientActivity)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(SmartSalesSuggestion)
except admin.sites.AlreadyRegistered:
    pass
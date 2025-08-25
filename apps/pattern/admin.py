from django.contrib import admin
from apps.pattern.models import *

# ✅ Auto-registered models
try:
    admin.site.register(PatternDesign)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(PatternPiece)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(PatternExecution)
except admin.sites.AlreadyRegistered:
    pass
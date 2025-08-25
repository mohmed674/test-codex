from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse, NoReverseMatch
from django.utils import timezone, translation
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache
from django.apps import apps
from django.test import Client
from django.utils.translation import gettext_lazy as _
from django.templatetags.static import static

from datetime import timedelta
import json
from dataclasses import dataclass
from typing import Optional, List

from core.utils.rendering import render_to_pdf_weasy
from core.utils.launcher import discover_apps

from .models import (
    JobTitle, Unit, EvaluationCriteria,
    ProductionStageType, RiskThreshold, DepartmentRole
)
from .forms import (
    JobTitleForm, UnitForm, EvaluationCriteriaForm,
    ProductionStageTypeForm, RiskThresholdForm, DepartmentRoleForm
)

# ==================== Helpers ====================

def safe_get_model(app_label: str, model_name: str):
    try:
        return apps.get_model(app_label, model_name)
    except Exception:
        return None

def count_risk_levels(IncidentModel):
    counts = {"high": 0, "medium": 0, "low": 0}
    if not IncidentModel:
        return counts
    fields = {f.name for f in IncidentModel._meta.get_fields()}
    qs = IncidentModel.objects.all()
    if "severity" in fields:
        counts["high"] = qs.filter(severity__iexact="high").count()
        counts["medium"] = qs.filter(severity__iexact="medium").count()
        counts["low"] = qs.filter(severity__iexact="low").count()
    elif "risk_level" in fields:
        counts["high"] = qs.filter(risk_level__iexact="high").count()
        counts["medium"] = qs.filter(risk_level__iexact="medium").count()
        counts["low"] = qs.filter(risk_level__iexact="low").count()
    return counts

def _build_admin_dashboard_context():
    SaleOrder            = safe_get_model('sales', 'SaleOrder')
    Payslip              = safe_get_model('payroll', 'Payslip')
    JournalEntry         = safe_get_model('accounting', 'JournalEntry')
    Evaluation           = safe_get_model('evaluation', 'Evaluation')
    AIDecisionLog        = safe_get_model('ai_decision', 'AIDecisionLog')
    InventoryDiscrepancy = safe_get_model('internal_monitoring', 'InventoryDiscrepancy')
    SuspiciousActivity   = safe_get_model('internal_monitoring', 'SuspiciousActivity')
    AutoPreventiveAction = safe_get_model('internal_monitoring', 'AutoPreventiveAction')
    RiskIncident         = safe_get_model('internal_monitoring', 'RiskIncident')

    now = timezone.now()
    last_week = now - timedelta(days=7)

    monitoring_data = {
        'discrepancies_count': InventoryDiscrepancy.objects.count() if InventoryDiscrepancy else 0,
        'recent_suspicious_count': SuspiciousActivity.objects.filter(timestamp__gte=last_week).count() if SuspiciousActivity else 0,
        'preventive_actions_count': AutoPreventiveAction.objects.filter(is_resolved=False).count() if AutoPreventiveAction else 0,
    }
    risk_counts = count_risk_levels(RiskIncident)
    context = {
        'total_sales':    SaleOrder.objects.count() if SaleOrder else 0,
        'total_revenue': (SaleOrder.objects.aggregate(Sum('total'))['total__sum'] or 0) if SaleOrder else 0,
        'total_expense': (JournalEntry.objects.filter(entry_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0) if JournalEntry else 0,
        'total_payslips': Payslip.objects.count() if Payslip else 0,
        'employee_evaluations': Evaluation.objects.count() if Evaluation else 0,
        'ai_alerts': AIDecisionLog.objects.count() if AIDecisionLog else 0,
        'monitoring_data': monitoring_data,
        'risk_data': json.dumps(risk_counts),
    }
    return context

# ---------- Launcher utils ----------
def _tile_to_dict(tile):
    if isinstance(tile, dict):
        return {
            "key": tile.get("key"),
            "name": tile.get("name"),
            "url": tile.get("url"),
            "icon_class": tile.get("icon_class") or "fas fa-cube",
            "category": tile.get("category"),
        }
    return {
        "key": getattr(tile, "key", None),
        "name": getattr(tile, "name", None),
        "url": getattr(tile, "url", None),
        "icon_class": getattr(tile, "icon_class", "fas fa-cube"),
        "category": getattr(tile, "category", None),
    }

# ---------- Table rows for _table_list.html ----------
@dataclass
class TableRow:
    cells: list
    edit_url: Optional[str] = None
    delete_url: Optional[str] = None
    def __iter__(self):
        return iter(self.cells)

def _lang_is_ar() -> bool:
    lang = translation.get_language() or "ar"
    return str(lang).lower().startswith("ar")

def _headers(*pairs: tuple) -> list:
    is_ar = _lang_is_ar()
    return [ar if is_ar else en for (ar, en) in pairs]

def _rev(name: str, **kwargs) -> Optional[str]:
    try:
        return reverse(name, kwargs=kwargs)
    except Exception:
        return None

def _norm(s: str) -> str:
    if not s: return ""
    # normalize arabic search: remove tatweel and diacritics
    return (
        s.strip().lower()
        .replace('\u0640', '')
        .translate(str.maketrans('', '', ''.join(chr(c) for c in range(0x064B, 0x0653))))
    )

# ==================== Launcher & Overview ====================
SECTIONS_META = [
    {"code":"sales",        "title_en":"Sales",        "title_ar":"المبيعات",   "color":"teal"},
    {"code":"procurement",  "title_en":"Procurement",  "title_ar":"المشتريات",  "color":"amber"},
    {"code":"inventory",    "title_en":"Inventory",    "title_ar":"المخزون",    "color":"green"},
    {"code":"manufacturing","title_en":"Manufacturing","title_ar":"التصنيع",    "color":"indigo"},
    {"code":"projects",     "title_en":"Projects",     "title_ar":"المشاريع",   "color":"blue"},
    {"code":"hr",           "title_en":"HR",           "title_ar":"الموارد",    "color":"rose"},
    {"code":"finance",      "title_en":"Finance",      "title_ar":"المالية",     "color":"violet"},
    {"code":"service",      "title_en":"Service",      "title_ar":"الدعم",       "color":"cyan"},
    {"code":"maintenance",  "title_en":"Maintenance",  "title_ar":"الصيانة",     "color":"slate"},
    {"code":"risk",         "title_en":"Risk",         "title_ar":"المخاطر",     "color":"brown"},
    {"code":"documents",    "title_en":"Documents",    "title_ar":"المستندات",   "color":"blue"},
    {"code":"marketing",    "title_en":"Marketing",    "title_ar":"التسويق",     "color":"orange"},
    {"code":"analytics",    "title_en":"Analytics",    "title_ar":"التحليلات",   "color":"purple"},
    {"code":"integrations", "title_en":"Integrations", "title_ar":"التكاملات",   "color":"cyan"},
    {"code":"portals",      "title_en":"Portals",      "title_ar":"البوابات",    "color":"indigo"},
    {"code":"system",       "title_en":"System",       "title_ar":"النظام",      "color":"slate"},
    {"code":"other",        "title_en":"Other",        "title_ar":"أخرى",        "color":"slate"},
]

SECTION_OF_KEY = {
    # System
    "core":"system", "theme_manager":"system", "dark_mode":"system", "colorfield":"system", "pattern":"system",

    # Sales & CRM
    "sales":"sales", "crm":"sales", "pos":"sales", "clients":"sales", "customers":"sales",

    # Procurement & Vendors
    "purchases":"procurement", "rfq":"procurement", "rfqs":"procurement", "suppliers":"procurement",

    # Portals
    "client_portal":"portals", "vendor_portal":"portals",

    # Inventory & Warehouse
    "inventory":"inventory", "warehouse_map":"inventory", "shipping":"inventory", "products":"inventory",

    # Manufacturing & PLM
    "mrp":"manufacturing", "production":"manufacturing", "plm":"manufacturing",

    # Projects & Tasks
    "projects":"projects", "workflow":"projects",

    # People & HR
    "hr":"hr", "employees":"hr", "attendance":"hr", "evaluation":"hr", "payroll":"hr",
    "departments":"hr", "discipline":"hr", "recruitment":"hr", "employee_monitoring":"hr",

    # Finance
    "accounting":"finance", "expenses":"finance",

    # Support & Service
    "support":"service",

    # Maintenance & Assets
    "maintenance":"maintenance", "asset_lifecycle":"maintenance",

    # Risk & Compliance / Monitoring
    "internal_monitoring":"risk", "monitoring":"risk", "risk_management":"risk",
    "work_regulations":"risk", "legal":"risk", "tracking":"risk",

    # Documents & Knowledge
    "document_center":"documents", "knowledge_center":"documents", "media":"documents", "contracts":"documents",

    # Marketing & Communication
    "campaigns":"marketing", "communication":"marketing", "communications":"marketing",
    "whatsapp_bot":"marketing", "notifications":"marketing", "voice_commands":"marketing",

    # Analytics & BI
    "bi":"analytics", "dashboard_center":"analytics", "demand_forecasting":"analytics", "ai_decision":"analytics",

    # Integrations & Sync
    "api_gateway":"integrations", "offline_sync":"integrations", "mobile":"integrations",
    "internal_bot":"integrations",
}
COLOR_BY_SECTION = {s["code"]: s["color"] for s in SECTIONS_META}

# ===== أيقونات ثابتة بناءً على الملفات المتاحة لديك (حرفيًا) =====
FALLBACK_ICON = "3dicons-moon-dynamic-color.png"
ICON_FILE_MAP = {
    # PLM & Manufacturing
    "plm":"plm.webp",
    "asset_lifecycle":"3d ico assetlifecyclens.webp",
    "mrp":"mrb.webp",
    "production":"3d icons production.webp",
    "manufacturing":"3d icons production.webp",

    # Sales
    "crm":"crm.jpg",
    "sales":"sales-awebp.webp",
    "pos":"pos.webp",
    "clients":"clients.jpg",
    "customers":"clients.jpg",  # لتفادي customers.jpg (غير موجود)
    "subscriptions":"survey.webp",
    "rental":"marketing 3d icons.jpg",  # أقرب ملف متاح

    # Finance
    "accounting":"accounting.webp",
    "expenses":"expenses.webp",
    "payroll":"payroll.png",
    "pyaroll":"pyaroll.png",

    # HR
    "hr":"hr.webp",
    "recruitment":"recruitment'.webp",
    "attendance":"attendance.jpg",
    "evaluation":"evaluation icon .jpg",
    "departments":"departments 3d icon.jpg",
    "employee_monitoring":"employee_monitoring.webp",
    "discipline":"3d icon disciplin.webp",

    # Logistics
    "inventory":"3d icons inventory.webp",
    "purchases":"3dicons-bag-dynamic-color.png",
    "suppliers":"suppliers.webp",
    "warehouse_map":"warehouse.webp",
    "shipping":"shipping .webp",
    "tracking":"tracking 3d icon.webp",

    # Operations
    "projects":"projects 3d icon.webp",
    "maintenance":"maintenance.jpg",
    "workflow":"workflow.png",
    "document_center":"document center.png",
    "contracts":"contracts 3d icon.webp",
    "products":"products.webp",
    "pattern":"pattern.webp",
    "signature":"signature.webp",

    # Risk & Compliance
    "risk_management":"risk management.webp",
    "internal_monitoring":"internal monitoring.webp",
    "monitoring":"monitoring.jpg",
    "legal":"3d icon legal.webp",
    "work_regulations":"work_regulations.webp",

    # Integrations & Channels
    "voice":"voice.webp",
    "voice_commands":"voice.webp",
    "whatsapp":"Whatsapp icon.jpg",
    "whatsapp_bot":"Whatsapp icon.jpg",
    "api_gateway":"api gateway.webp",
    "mobile":"mobile.webp",
    "client_portal":"3d icons client portal.webp",
    "vendor_portal":"3d png 3d icon vendor portal.webp",
    "communication":"communication.webp",
    "campaigns":"campaigns.webp",

    # Admin / Utilities / BI / Others
    "dashboard_center":"dashboard.webp",
    "backup_center":"backup-server-.webp",
    "dark_mode":"3dicons-moon-dynamic-color.png",
    "theme_manager":"themes.png",
    "colorfield":"themes.png",  # لا يوجد flash icon في قائمتك، نستخدم themes.png
    "bi":"BI 3d icon.webp",
    "support":"Call Center PNG.jpg",
    "media":"Colorful 3D Cartoon Megaphone Announcement .jpg",  # أقرب بديل مرئي متاح
    "website":"ecommerce 3d icons.jpg",  # إن وُجد المفتاح
    "ecommerce":"ecommerce 3d icons.jpg",
    "notifications":"notifications.webp",
    "demand_forecasting":"demand forecasting .webp",
    "core":"core .jpg",
    "knowledge_center":"knowledge 3d icon.webp",
    "internal_bot":"internal bot .webp",
    "ai_decision":"copilot.png",
    "rfq":"rfqs.jpg",
    "rfqs":"rfqs.jpg",
    "marketing":"marketing.jpg",
    "offline_sync":"offline sync.webp",
    "survey":"survey.webp",
}

# تسميات عربية قسرية لبعض التايلات
AR_OVERRIDES = {
    "core": "الإعدادات",
    "theme_manager": "مدير القوالب",
    "dark_mode": "الوضع الليلي",
    "colorfield": "الألوان",
}

def _icon_url_for(key: str) -> str:
    """أعد مسار الأيقونة الثابت حسب الخريطة؛ وإلا أعِد fallback الموجود فعليًا."""
    fname = ICON_FILE_MAP.get((key or "").strip().lower())
    if fname:
        return static(f'icons/3d/{fname}')
    return static(f'icons/3d/{FALLBACK_ICON}')

POSSIBLE_ENTRY_NAMES = (
    '{k}:index', '{k}:home', '{k}:dashboard', '{k}:list', '{k}:overview',
    '{k}_index', '{k}_home', '{k}'
)

def _resolve_url_for(key: str, given_url: Optional[str]) -> str:
    if given_url:
        return given_url
    # نحاول اسماء قياسية
    for pat in POSSIBLE_ENTRY_NAMES:
        name = pat.format(k=key)
        try:
            return reverse(name)
        except NoReverseMatch:
            continue
    # بعض التطبيقات قد تُسمى بدون namespace
    try:
        return reverse(f'{key}-index')
    except NoReverseMatch:
        return '#'

def _filter_apps(apps_list: List[dict], query: Optional[str]) -> List[dict]:
    qn = _norm(query or '')
    if not qn:
        return apps_list
    res = []
    for a in apps_list:
        val = _norm(a.get("name","")) + " " + _norm(a.get("key",""))
        if qn in val:
            res.append(a)
    return res

@login_required
@never_cache
def launcher_view(request):
    tiles = discover_apps()
    is_ar = _lang_is_ar()
    q = request.GET.get("q")

    # توحيد البيانات وتمرير icon_url وروابط سليمة
    raw_apps: List[dict] = []
    for t in tiles:
        d = _tile_to_dict(t)
        key = (d.get("key") or "").strip().lower()
        name = d.get("name") or key or ""
        if is_ar:
            name = AR_OVERRIDES.get(key, name)
        url = _resolve_url_for(key, d.get("url"))
        icon_url = _icon_url_for(key)
        sec_code = SECTION_OF_KEY.get(key, "other")
        raw_apps.append({
            "key":   key,
            "name":  name,
            "url":   url,
            "disabled": (url == "#"),
            "icon_class": d.get("icon_class") or "fas fa-cube",
            "icon_url": icon_url,
            "section": sec_code,
            "color": COLOR_BY_SECTION.get(sec_code, "slate"),
        })

    # فلترة حسب q
    filtered_apps = _filter_apps(raw_apps, q)

    # تجميع حسب الأقسام
    grouped = {s["code"]: [] for s in SECTIONS_META}
    for app in filtered_apps:
        grouped.setdefault(app["section"], []).append({
            "key": app["key"],
            "name": app["name"],
            "url": app["url"],
            "disabled": app["disabled"],
            "icon_class": app["icon_class"],
            "icon_url": app["icon_url"],
            "color": app["color"],
        })

    sections: List[dict] = []
    for s in SECTIONS_META:
        items = grouped.get(s["code"], [])
        if not items:
            continue
        sections.append({
            "code": s["code"],
            "title_en": s["title_en"],
            "title_ar": s["title_ar"],
            "items": items,
        })

    lang = translation.get_language() or "ar"
    ctx = {
        "apps": filtered_apps,
        "apps_count": len(filtered_apps),
        "q": q or "",
        "sections": sections,
        "lang": "ar" if str(lang).lower().startswith("ar") else "en",
        "dir": "rtl" if str(lang).lower().startswith("ar") else "ltr",
        "title": "لوحة التطبيقات" if str(lang).lower().startswith("ar") else "Applications",
    }
    return render(request, "core/launcher.html", ctx)

# ==================== Aliases ====================

@login_required
def launcher(request):
    return launcher_view(request)

@login_required
def launcher_alias(request):
    return launcher_view(request)

# ==================== Overview ====================

@login_required
@never_cache
def overview_view(request):
    SaleInvoice = safe_get_model('sales', 'SaleInvoice') or safe_get_model('sales', 'SaleOrder')
    CashTxn     = safe_get_model('accounting', 'CashTransaction')
    Product     = safe_get_model('products', 'Product')
    ClientM     = safe_get_model('clients', 'Client')
    EmployeeM   = safe_get_model('employees', 'Employee')

    total_sales = (SaleInvoice.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0) if SaleInvoice else 0
    total_transactions = (CashTxn.objects.aggregate(Sum('amount'))['amount__sum'] or 0) if CashTxn else 0
    total_products = Product.objects.count() if Product else 0
    total_clients = ClientM.objects.count() if ClientM else 0
    total_employees = EmployeeM.objects.count() if EmployeeM else 0

    # نفس الريجيستري المستخدم في اللانشر + بحث q
    tiles = discover_apps()
    q = request.GET.get("q")

    apps_cards: List[dict] = []
    for t in tiles:
        d = _tile_to_dict(t)
        key = (d.get("key") or "").strip().lower()
        name = d.get("name") or key or ""
        url = _resolve_url_for(key, d.get("url"))
        icon_url = _icon_url_for(key)
        apps_cards.append({
            "key": key,
            "name": name,
            "url": url,
            "disabled": (url == "#"),
            "icon_class": d.get("icon_class") or "fas fa-cube",
            "icon_url": icon_url,
        })

    apps_cards = _filter_apps(apps_cards, q)

    ctx = {
        "kpis": {
            "total_sales": total_sales,
            "total_transactions": total_transactions,
            "total_products": total_products,
            "total_clients": total_clients,
            "total_employees": total_employees,
        },
        "apps": apps_cards,
        "apps_count": len(apps_cards),
        "q": q or "",
    }
    return render(request, 'core/overview.html', ctx)

# ==================== Dashboards ====================

@login_required
def dashboard(request):
    tiles = discover_apps()
    apps_ctx = []
    for t in tiles:
        d = _tile_to_dict(t)
        key = (d.get("key") or "").strip().lower()
        apps_ctx.append({
            "name": d["name"],
            "url": _resolve_url_for(key, d["url"]),
            "icon": d["icon_class"],
            "icon_url": _icon_url_for(key),
            "disabled": _resolve_url_for(key, d["url"]) == "#",
        })
    widgets = [
        {"icon": "fas fa-users", "title": _("عدد الموظفين"), "value": "—"},
        {"icon": "fas fa-boxes", "title": _("أصناف المخزون"), "value": "—"},
        {"icon": "fas fa-receipt", "title": _("طلبات اليوم"), "value": "—"},
    ]
    return render(request, "core/dashboard.html", {"widgets": widgets, "apps": apps_ctx})

@login_required
def smart_master_dashboard(request):
    return render(request, 'core/smart_dashboard.html')

@login_required
def admin_dashboard_view(request):
    context = _build_admin_dashboard_context()
    return render(request, 'core/admin_dashboard.html', context)

@login_required
def admin_dashboard_pdf_view(request):
    context = _build_admin_dashboard_context()
    return render_to_pdf_weasy("core/admin_dashboard_pdf.html", context, filename="dashboard_report.pdf")

# ==================== Masters CRUD + Partial-ready Context ====================

# ---- JobTitle ----
@login_required
def job_title_list(request):
    titles = JobTitle.objects.all()
    headers = _headers(("#", "#"), ("المسمى الوظيفي", "Job Title"))
    rows: List[TableRow] = []
    for t in titles:
        rows.append(TableRow(
            cells=[None, getattr(t, "name", None) or getattr(t, "title", str(t))],
            edit_url=_rev('core:job_title_update', pk=t.pk),
            delete_url=_rev('core:job_title_delete', pk=t.pk),
        ))
    return render(request, 'core/job_title_list.html', {
        'titles': titles, 'headers': headers, 'objects': rows
    })

@login_required
def job_title_create(request):
    form = JobTitleForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('core:job_title_list')
    return render(request, 'core/job_title_form.html', {'form': form})

@login_required
def job_title_update(request, pk):
    obj = get_object_or_404(JobTitle, pk=pk)
    form = JobTitleForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect('core:job_title_list')
    return render(request, 'core/job_title_form.html', {'form': form, 'object': obj})

@login_required
@require_POST
def job_title_delete(request, pk):
    JobTitle.objects.filter(pk=pk).delete()
    return redirect('core:job_title_list')

# ---- Unit ----
@login_required
def unit_list(request):
    units = Unit.objects.all()
    headers = _headers(
        ("#", "#"), ("اسم الوحدة", "Unit Name"), ("الاختصار", "Abbreviation"),
        ("نوع الوحدة", "Unit Type"), ("نشِطة", "Active"), ("وحدة مجمعة", "Bulk Unit")
    )
    rows: List[TableRow] = []
    for u in units:
        utype = u.get_unit_type_display() if hasattr(u, "get_unit_type_display") else getattr(u, "unit_type", "—")
        rows.append(TableRow(
            cells=[
                None, getattr(u, "name", str(u)),
                getattr(u, "abbreviation", "") or "—",
                utype or "—",
                "✅" if getattr(u, "is_active", False) else "❌",
                _("مجمّعة") if getattr(u, "is_bulk_unit", False) else "—",
            ],
            edit_url=_rev('core:unit_update', pk=u.pk),
            delete_url=_rev('core:unit_delete', pk=u.pk),
        ))
    return render(request, 'core/unit_list.html', {
        'units': units, 'headers': headers, 'objects': rows
    })

@login_required
def unit_create(request):
    form = UnitForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('core:unit_list')
    return render(request, 'core/unit_form.html', {'form': form})

@login_required
def unit_update(request, pk):
    obj = get_object_or_404(Unit, pk=pk)
    form = UnitForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect('core:unit_list')
    return render(request, 'core/unit_form.html', {'form': form, 'object': obj})

@login_required
@require_POST
def unit_delete(request, pk):
    Unit.objects.filter(pk=pk).delete()
    return redirect('core:unit_list')

# ---- EvaluationCriteria ----
@login_required
def criteria_list(request):
    criteria = EvaluationCriteria.objects.all()
    headers = _headers(("#", "#"), ("الاسم", "Name"), ("النوع", "Type"), ("الوزن", "Weight"), ("نشِط", "Active"))
    rows: List[TableRow] = []
    for c in criteria:
        ctype = c.get_criteria_type_display() if hasattr(c, "get_criteria_type_display") else getattr(c, "criteria_type", "—")
        rows.append(TableRow(
            cells=[
                None, getattr(c, "name", str(c)),
                ctype or "—",
                getattr(c, "weight", None) if getattr(c, "weight", None) is not None else "—",
                "✅" if getattr(c, "is_active", False) else "❌",
            ],
            edit_url=_rev('core:criteria_update', pk=c.pk),
            delete_url=_rev('core:criteria_delete', pk=c.pk),
        ))
    return render(request, 'core/criteria_list.html', {
        'criteria': criteria, 'headers': headers, 'objects': rows
    })

@login_required
def criteria_create(request):
    form = EvaluationCriteriaForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('core:criteria_list')
    return render(request, 'core/criteria_form.html', {'form': form})

@login_required
def criteria_update(request, pk):
    obj = get_object_or_404(EvaluationCriteria, pk=pk)
    form = EvaluationCriteriaForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect('core:criteria_list')
    return render(request, 'core/criteria_form.html', {'form': form, 'object': obj})

@login_required
@require_POST
def criteria_delete(request, pk):
    EvaluationCriteria.objects.filter(pk=pk).delete()
    return redirect('core:criteria_list')

# ---- ProductionStageType ----
@login_required
def stage_type_list(request):
    stages = ProductionStageType.objects.all()
    headers = _headers(
        ("#", "#"), ("الاسم", "Name"), ("الترتيب", "Order"),
        ("المدة التقديرية (دقائق)", "Est. Duration (min)"),
        ("تتطلب ماكينة", "Requires Machine"), ("نشِطة", "Active")
    )
    rows: List[TableRow] = []
    for s in stages:
        rows.append(TableRow(
            cells=[
                None,
                getattr(s, "name", str(s)),
                getattr(s, "order", None) if getattr(s, "order", None) is not None else "—",
                getattr(s, "estimated_duration_minutes", None) if getattr(s, "estimated_duration_minutes", None) is not None else "—",
                "🛠️" if getattr(s, "requires_machine", False) else "—",
                "✅" if getattr(s, "is_active", False) else "❌",
            ],
            edit_url=_rev('core:stage_type_update', pk=s.pk),
            delete_url=_rev('core:stage_type_delete', pk=s.pk),
        ))
    return render(request, 'core/stage_type_list.html', {
        'stages': stages, 'headers': headers, 'objects': rows
    })

@login_required
def stage_type_create(request, pk=None):
    form = ProductionStageTypeForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('core:stage_type_list')
    return render(request, 'core/stage_type_form.html', {'form': form})

@login_required
def stage_type_update(request, pk):
    obj = get_object_or_404(ProductionStageType, pk=pk)
    form = ProductionStageTypeForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect('core:stage_type_list')
    return render(request, 'core/stage_type_form.html', {'form': form, 'object': obj})

@login_required
@require_POST
def stage_type_delete(request, pk):
    ProductionStageType.objects.filter(pk=pk).delete()
    return redirect('core:stage_type_list')

# ---- RiskThreshold ----
@login_required
def risk_threshold_list(request):
    risks = RiskThreshold.objects.all()
    headers = _headers(("#", "#"), ("نوع الخطر", "Risk Type"), ("القيمة الحدية", "Threshold Value"), ("الخطورة", "Severity"), ("نشط", "Active"))
    rows: List[TableRow] = []
    for r in risks:
        sev = r.get_severity_level_display() if hasattr(r, "get_severity_level_display") else getattr(r, "severity_level", "—")
        rows.append(TableRow(
            cells=[
                None,
                getattr(r, "risk_type", str(r)),
                getattr(r, "threshold_value", "—"),
                sev or "—",
                "✅" if getattr(r, "is_active", False) else "❌",
            ],
            edit_url=_rev('core:risk_threshold_update', pk=r.pk),
            delete_url=_rev('core:risk_threshold_delete', pk=r.pk),
        ))
    return render(request, 'core/risk_threshold_list.html', {
        'risks': risks, 'headers': headers, 'objects': rows
    })

@login_required
def risk_threshold_create(request):
    form = RiskThresholdForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('core:risk_threshold_list')
    return render(request, 'core/risk_threshold_form.html', {'form': form})

@login_required
def risk_threshold_update(request, pk):
    obj = get_object_or_404(RiskThreshold, pk=pk)
    form = RiskThresholdForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect('core:risk_threshold_list')
    return render(request, 'core/risk_threshold_form.html', {'form': form, 'object': obj})

@login_required
@require_POST
def risk_threshold_delete(request, pk):
    RiskThreshold.objects.filter(pk=pk).delete()
    return redirect('core:risk_threshold_list')

# ---- DepartmentRole ----
@login_required
def department_role_list(request):
    roles = DepartmentRole.objects.all()
    headers = _headers(("#", "#"), ("الاسم", "Name"))
    rows: List[TableRow] = []
    for r in roles:
        rows.append(TableRow(
            cells=[None, getattr(r, "name", str(r))],
            edit_url=_rev('core:department_role_update', pk=r.pk),
            delete_url=_rev('core:department_role_delete', pk=r.pk),
        ))
    return render(request, 'core/department_role_list.html', {
        'roles': roles, 'headers': headers, 'objects': rows
    })

@login_required
def department_role_create(request):
    form = DepartmentRoleForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('core:department_role_list')
    return render(request, 'core/department_role_form.html', {'form': form})

@login_required
def department_role_update(request, pk):
    obj = get_object_or_404(DepartmentRole, pk=pk)
    form = DepartmentRoleForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect('core:department_role_list')
    return render(request, 'core/department_role_form.html', {'form': form, 'object': obj})

@login_required
@require_POST
def department_role_delete(request, pk):
    DepartmentRole.objects.filter(pk=pk).delete()
    return redirect('core:department_role_list')

# ==================== Payments (Placeholder) ====================

@login_required
@require_POST
def initiate_fawry_payment(request):
    return JsonResponse(
        {"detail": "Fawry integration is not enabled in this build.",
         "hint": "Replace this with real integration when ready."},
        status=501
    )

# ==================== Utilities / Debug ====================

@user_passes_test(lambda u: u.is_staff)
@login_required
def urls_health(request):
    tiles = discover_apps()
    client = Client()
    report = []
    for t in tiles:
        d = _tile_to_dict(t)
        url = _resolve_url_for((d.get("key") or "").strip().lower(), d["url"])
        try:
            r = client.get(url)
            code = r.status_code
        except Exception:
            code = 0
        report.append({"name": d["name"], "url": url, "status": code})
    return JsonResponse({"items": report})

@user_passes_test(lambda u: u.is_staff)
@login_required
def apps_debug(request):
    tiles = discover_apps()
    data = []
    for t in tiles:
        d = _tile_to_dict(t)
        key = (d.get("key") or "").strip().lower()
        data.append({
            **d,
            "resolved_url": _resolve_url_for(key, d.get("url")),
            "icon_url": _icon_url_for(key),
        })
    return JsonResponse({"count": len(data), "apps": data})

@user_passes_test(lambda u: u.is_staff)
@login_required
def launcher_keys_debug(request):
    try:
        from core.utils.launcher import LABELS
    except Exception:
        LABELS = {"ar": {}, "en": {}}
    tiles = discover_apps()
    data = [_tile_to_dict(t) for t in tiles]
    keys = [d["key"] for d in data if d.get("key")]
    lang = translation.get_language()
    missing_ar = [k for k in keys if k not in LABELS.get("ar", {})]
    missing_en = [k for k in keys if k not in LABELS.get("en", {})]
    return JsonResponse({
        "lang": lang, "count": len(data), "items": data,
        "missing_ar": missing_ar, "missing_en": missing_en,
    })

# ==================== PWA / Offline helpers ====================

@never_cache
def offline(request):
    """عرض صفحة العمل دون اتصال لاختبارها أثناء الاتصال أيضاً."""
    return render(request, 'core/offline.html')

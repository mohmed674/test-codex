# core/utils/launcher.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Dict, Set, Tuple
import re

from django.urls import get_resolver, reverse, NoReverseMatch
from django.urls.resolvers import URLResolver, URLPattern
from django.utils import translation

# أسماء صفحات البداية المحتملة داخل كل تطبيق
CANDIDATE_NAMES: Tuple[str, ...] = (
    "overview", "dashboard", "home", "index",
    "main", "main_dashboard", "list", "launcher"
)

# مسميات/نيمسبيسات يجب تجاهلها + أنماط URLs غير تطبيقات (favicon/API العامة..)
SKIP_KEYS: Set[str] = {
    "admin", "i18n", "static", "media",
    # تطبيقات ليست من منظومتك
    "auth", "django_celery_beat", "django_celery_results", "suppliers_api",
}
SKIP_URL_ENDS: Tuple[str, ...] = (".ico",)
SKIP_URL_PREFIXES: Tuple[str, ...] = (
    "/api/", "/auth/", "/django_celery_beat/", "/django_celery_results/",
)

# أيقونات افتراضية (Font Awesome)
ICON_MAP: Dict[str, str] = {
    "ai": "fas fa-brain",
    "ai_decision": "fas fa-brain",
    "api_gateway": "fas fa-cloud",
    "asset_lifecycle": "fas fa-recycle",
    "attendance": "fas fa-calendar-check",
    "backup_center": "fas fa-database",
    "bi": "fas fa-chart-line",
    "campaigns": "fas fa-bullhorn",
    "client_portal": "fas fa-door-open",
    "clients": "fas fa-users",
    "communication": "fas fa-comments",
    "contracts": "fas fa-file-contract",
    "core": "fas fa-cube",
    "crm": "fas fa-address-book",
    "dashboard_center": "fas fa-chart-pie",
    "departments": "fas fa-sitemap",
    "discipline": "fas fa-user-shield",
    "document_center": "fas fa-folder-open",
    "employees": "fas fa-user-tie",
    "employee_monitoring": "fas fa-user-check",
    "evaluation": "fas fa-star-half-alt",
    "expenses": "fas fa-file-invoice-dollar",
    "internal_bot": "fas fa-robot",
    "internal_monitoring": "fas fa-shield-alt",
    "inventory": "fas fa-warehouse",
    "knowledge_center": "fas fa-book",
    "legal": "fas fa-scale-balanced",
    "maintenance": "fas fa-tools",
    "mobile": "fas fa-mobile-screen",
    "monitoring": "fas fa-eye",
    "mrp": "fas fa-gears",
    "notifications": "fas fa-bell",
    "offline_sync": "fas fa-arrows-rotate",
    "pattern": "fas fa-ruler-combined",
    "payroll": "fas fa-money-check-dollar",
    "pos": "fas fa-cash-register",
    "products": "fas fa-box-open",
    "production": "fas fa-industry",
    "projects": "fas fa-diagram-project",
    "purchases": "fas fa-truck",
    "recruitment": "fas fa-user-plus",
    "rfq": "fas fa-file-circle-question",
    "risk_management": "fas fa-triangle-exclamation",
    "sales": "fas fa-shopping-cart",
    "shipping": "fas fa-truck-ramp-box",
    "suppliers": "fas fa-truck-moving",
    "support": "fas fa-headset",
    "survey": "fas fa-clipboard-list",
    "tracking": "fas fa-location-dot",
    "vendor_portal": "fas fa-handshake",
    "voice_commands": "fas fa-microphone",
    "warehouse_map": "fas fa-map-location-dot",
    "whatsapp_bot": "fab fa-whatsapp",
    "work_regulations": "fas fa-file-shield",
    "workflow": "fas fa-diagram-next",
    "accounting": "fas fa-calculator",
    "demand_forecasting": "fas fa-chart-area",
    "media": "fas fa-photo-film",
    "theme_manager": "fas fa-palette",
    "dark_mode": "fas fa-moon",
    "colorfield": "fas fa-fill-drip",

    # مفاتيح أساسية
    "hr": "fas fa-user-group",
    "plm": "fas fa-diagram-project",
}

# تسميات ثابتة باللغتين
LABELS: Dict[str, Dict[str, str]] = {
    "en": {
        "ai": "AI", "ai_decision": "Copilot", "api_gateway": "API Gateway",
        "asset_lifecycle": "Asset Lifecycle", "attendance": "Attendance",
        "backup_center": "Backup Center", "bi": "BI", "campaigns": "Campaigns",
        "client_portal": "Client Portal", "clients": "Customers",
        "communication": "Communications", "contracts": "Contracts",
        "core": "Core", "crm": "CRM", "dashboard_center": "Dashboards",
        "departments": "Departments", "discipline": "Discipline",
        "document_center": "Document Center", "employees": "HR",
        "employee_monitoring": "Employee Monitoring", "evaluation": "Evaluation",
        "expenses": "Expenses", "internal_bot": "Internal Bot",
        "internal_monitoring": "Internal Monitoring", "inventory": "Inventory",
        "knowledge_center": "Knowledge Center", "legal": "Legal",
        "maintenance": "Maintenance", "mobile": "Mobile App",
        "monitoring": "Monitoring", "mrp": "MRP", "notifications": "Notifications",
        "offline_sync": "Offline Sync", "pattern": "Pattern", "payroll": "Payroll",
        "pos": "POS", "products": "Products", "production": "Production",
        "projects": "Projects", "purchases": "Purchases", "recruitment": "Recruitment",
        "rfq": "RFQs", "risk_management": "Risk Management", "sales": "Sales",
        "shipping": "Shipping", "suppliers": "Suppliers", "support": "Support",
        "survey": "Survey", "tracking": "Tracking", "vendor_portal": "Vendor Portal",
        "voice_commands": "Voice", "warehouse_map": "Warehouse Map",
        "whatsapp_bot": "WhatsApp", "work_regulations": "Work Regulations",
        "workflow": "Workflow", "accounting": "Accounting",
        "demand_forecasting": "Demand Forecasting", "media": "Media",
        "departments_roles": "Department Roles",
        "hr": "HR", "plm": "PLM",
    },
    "ar": {
        "ai": "الذكاء الاصطناعي", "ai_decision": "المساعد الذكي", "api_gateway": "بوابة API",
        "asset_lifecycle": "دورة حياة الأصول", "attendance": "الحضور والانصراف",
        "backup_center": "مركز النسخ الاحتياطي", "bi": "ذكاء الأعمال", "campaigns": "الحملات",
        "client_portal": "بوابة العميل", "clients": "العملاء", "communication": "الاتصالات",
        "contracts": "العقود", "core": "النواة", "crm": "إدارة العلاقات",
        "dashboard_center": "لوحات التحكم", "departments": "الأقسام",
        "discipline": "الجزاءات", "document_center": "مركز المستندات",
        "employees": "الموارد البشرية", "employee_monitoring": "مراقبة الموظفين",
        "evaluation": "التقييم", "expenses": "المصروفات", "internal_bot": "البوت الداخلي",
        "internal_monitoring": "المراقبة الداخلية", "inventory": "المخزون",
        "knowledge_center": "مركز المعرفة", "legal": "الشؤون القانونية",
        "maintenance": "الصيانة", "mobile": "تطبيق الجوال", "monitoring": "المراقبة",
        "mrp": "التصنيع", "notifications": "الإشعارات", "offline_sync": "المزامنة دون اتصال",
        "pattern": "الباترون", "payroll": "الرواتب", "pos": "نقطة البيع",
        "products": "المنتجات", "production": "الإنتاج", "projects": "المشاريع",
        "purchases": "المشتريات", "recruitment": "التوظيف", "rfq": "طلبات عروض الأسعار",
        "risk_management": "إدارة المخاطر", "sales": "المبيعات", "shipping": "الشحن",
        "suppliers": "الموردون", "support": "الدعم الفني", "survey": "الاستبيانات",
        "tracking": "التتبع", "vendor_portal": "بوابة المورد", "voice_commands": "الأوامر الصوتية",
        "warehouse_map": "خريطة المخازن", "whatsapp_bot": "واتساب",
        "work_regulations": "لوائح العمل", "workflow": "سير العمل",
        "accounting": "المحاسبة", "demand_forecasting": "التنبؤ بالطلب",
        "media": "الوسائط", "departments_roles": "أدوار الأقسام",
        # المطلوب: PLM بالعربية
        "hr": "الموارد البشرية",
        "plm": "إدارة دورة حياة المنتج",
    },
}

# تطبيع أسماء المفاتيح
NORMALIZE_MAP: Dict[str, str] = {
    "customer": "clients", "customers": "clients", "client": "clients",
    "vendor": "suppliers", "vendors": "suppliers",
    "ai-decision": "ai_decision", "ai_decisions": "ai_decision", "ai": "ai_decision",
    "copilot": "ai_decision",
    "whatsapp": "whatsapp_bot",
    "dashboards": "dashboard_center", "dashboard": "dashboard_center",
    "docs": "document_center", "documents": "document_center",
    "knowledge": "knowledge_center",
    "voice": "voice_commands", "voice-commands": "voice_commands",
    "warehouse": "warehouse_map", "workregulations": "work_regulations",
    "client-portal": "client_portal", "api-gateway": "api_gateway",
    "asset-lifecycle": "asset_lifecycle", "backup-center": "backup_center",
    "document-center": "document_center", "internal-bot": "internal_bot",
    "internal-bot ": "internal_bot", "internal-monitoring": "internal_monitoring",
    "offline-sync": "offline_sync", "risk-management": "risk_management",
    "vendor-portal": "vendor_portal", "warehouse-map": "warehouse_map",
    "work-regulations": "work_regulations",
    # شائعة
    "employees": "hr", "hr-app": "hr", "product": "products", "communications": "communication",
    "notifactions": "notifications",
    "product-lifecycle": "plm", "product_lifecycle": "plm", "product_lifecycle_management": "plm",
}

@dataclass(frozen=True)
class DiscoveredTile:
    key: str
    url: str
    icon_class: str
    name: str

def _current_lang() -> str:
    lang = translation.get_language() or "ar"
    return "ar" if str(lang).lower().startswith("ar") else "en"

def _normalize_key(key: str) -> str:
    k = (key or "").strip().lower().strip("/").replace("-", "_")
    return NORMALIZE_MAP.get(k, k)

_alnum_re = re.compile(r"^[a-z0-9_]{2,}$")  # مفاتيح مقبولة فقط

def _allowed_key(key: str) -> bool:
    """السماح فقط بالمفاتيح المعرفة لدينا لمنع ظهور عناصر ليست من التطبيقات."""
    return (
        bool(_alnum_re.match(key)) and
        (key in ICON_MAP or key in LABELS["en"] or key in LABELS["ar"])
    )

def _first_working_url(namespace: Optional[str], candidate_names: Iterable[str]) -> Optional[str]:
    for name in candidate_names:
        if namespace:
            try:
                return reverse(f"{namespace}:{name}")
            except NoReverseMatch:
                pass
        try:
            return reverse(name)
        except NoReverseMatch:
            pass
    return None

def _label_for(raw_key: str) -> str:
    lang = _current_lang()
    key = _normalize_key(raw_key)
    return (
        LABELS.get(lang, {}).get(key)
        or LABELS.get("ar" if lang == "en" else "en", {}).get(key)
        or key.replace("_", " ").title()
    )

def _collect_named_patterns(resolver: URLResolver) -> Set[str]:
    names: Set[str] = set()
    for ip in getattr(resolver, "url_patterns", []):
        if isinstance(ip, URLPattern) and ip.name:
            names.add(ip.name)
    return names

def _walk_resolvers(resolver: URLResolver) -> List[URLResolver]:
    out: List[URLResolver] = []
    stack: List[URLResolver] = [resolver]
    seen: Set[int] = set()
    while stack:
        cur = stack.pop()
        if id(cur) in seen:
            continue
        seen.add(id(cur))
        out.append(cur)
        for p in getattr(cur, "url_patterns", []):
            if isinstance(p, URLResolver):
                stack.append(p)
    return out

def _scan_all() -> List[DiscoveredTile]:
    root = get_resolver()
    tiles: List[DiscoveredTile] = []

    for resolver in _walk_resolvers(root):
        ns = resolver.namespace or getattr(resolver, "namespace", None) or getattr(resolver.urlconf_module, "app_name", None)
        prefix = str(getattr(resolver, "pattern", ""))

        key_seed = ns or (prefix.strip("/").split("/")[0] if prefix.strip("/") else "")
        key_guess = _normalize_key(key_seed)

        # تجاهل مفاتيح وأنماط غير مرغوبة
        if not key_guess or key_guess in SKIP_KEYS or not _allowed_key(key_guess):
            continue

        inner_names = _collect_named_patterns(resolver)
        ordered_candidates = [n for n in CANDIDATE_NAMES if n in inner_names] + list(inner_names)

        url = _first_working_url(ns, ordered_candidates) or ("/" + prefix.lstrip("/"))
        if not url:
            continue
        # تجاهل favicon وواجهات API العامة
        if url.endswith(SKIP_URL_ENDS) or "favicon.ico" in url:
            continue
        if url == "/" or url in {"/api", "/api/"}:
            continue
        if any(url.startswith(p) for p in SKIP_URL_PREFIXES) and key_guess != "api_gateway":
            continue

        name = _label_for(key_guess)
        icon = ICON_MAP.get(key_guess, "fas fa-cube")

        tiles.append(DiscoveredTile(
            key=key_guess,
            url=url,
            icon_class=icon,
            name=name
        ))

    # إزالة التكرارات بنفس المفتاح/الرابط
    uniq_by_key: Dict[str, DiscoveredTile] = {}
    seen_urls: Set[str] = set()
    for t in tiles:
        if t.key in uniq_by_key or t.url in seen_urls:
            continue
        uniq_by_key[t.key] = t
        seen_urls.add(t.url)

    final = list(uniq_by_key.values())
    final.sort(key=lambda x: str(x.name).lower())
    return final

def discover_apps() -> List[Dict[str, str]]:
    tiles = _scan_all()
    return [{
        "key": t.key,
        "name": t.name,
        "url": t.url,
        "icon_class": t.icon_class,
    } for t in tiles]

def debug_urls() -> None:
    tiles = discover_apps()
    print("=== DISCOVERED APPS ===")
    for a in tiles:
        print(f"- {a['key']:<20} {a['name']:<22} -> {a['url']:<30} ({a['icon_class']})")

__all__ = ["discover_apps", "debug_urls", "LABELS"]

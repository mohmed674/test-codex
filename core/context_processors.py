from django.urls import reverse, NoReverseMatch
from django.conf import settings

def apps_list(request):
    """
    يُرجع قائمة بالتطبيقات التي لها مسار URL صالح واسم أيقونة.
    عدّل dicts أدناه بحسب apps و icons الموجودة فعلياً في مشروعك.
    """
    raw = [
        {"name": "الموارد البشرية", "url_name": "employees:list", "icon": "fa-user-tie"},
        {"name": "الحضور والانصراف", "url_name": "attendance:list", "icon": "fa-calendar-check"},
        {"name": "الرواتب", "url_name": "payroll:list", "icon": "fa-money-check-alt"},
        {"name": "الإنتاج", "url_name": "production:list", "icon": "fa-industry"},
        {"name": "المنتجات", "url_name": "products:list", "icon": "fa-box-open"},
        {"name": "المخزون", "url_name": "inventory:list", "icon": "fa-warehouse"},
        {"name": "المبيعات", "url_name": "sales:list", "icon": "fa-shopping-cart"},
        {"name": "المشتريات", "url_name": "purchases:list", "icon": "fa-truck"},
        {"name": "العملاء", "url_name": "clients:list", "icon": "fa-users"},
        {"name": "المحاسبة", "url_name": "accounting:reports_overview", "icon": "fa-calculator"},
        {"name": "التسويق", "url_name": "marketing:dashboard", "icon": "fa-bullhorn"},
        {"name": "الذكاء الاصطناعي", "url_name": "ai_dashboard", "icon": "fa-brain"},
        {"name": "الصيانة", "url_name": "maintenance:list", "icon": "fa-tools"},
        {"name": "الموردين", "url_name": "suppliers:list", "icon": "fa-truck-moving"},
        {"name": "العقود", "url_name": "contracts:list", "icon": "fa-file-contract"},
        {"name": "تسجيل الخروج", "url_name": "logout", "icon": "fa-sign-out-alt", "danger": True},
    ]
    apps = []
    for a in raw:
        try:
            url = reverse(a["url_name"])
        except NoReverseMatch:
            continue
        apps.append({
            "name": a["name"],
            "url": url,
            "icon": a["icon"],
            "danger": a.get("danger", False),
        })
    return {"apps_list": apps}

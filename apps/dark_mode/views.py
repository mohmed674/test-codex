from django.shortcuts import redirect, render
from django.urls import reverse
from django.template.loader import get_template
from django.template import TemplateDoesNotExist

def toggle_dark_mode(request):
    current = request.session.get("dark_mode", False)
    request.session["dark_mode"] = not current
    return redirect(request.META.get("HTTP_REFERER", "/"))

def overview(request):
    """
    فتح صفحة الوضع الليلي مع سقوط آمن:
    1) يحاول dark_mode/overview.html
    2) ثم theme_manager/overview.html
    3) وإلا يُحوِّل لنظرة عامة النظام core:overview (ثم اللانشر كملاذ أخير)
    """
    # 1) قالب التطبيق نفسه (إن وُجد)
    try:
        get_template('dark_mode/overview.html')
        return render(request, 'dark_mode/overview.html', {})
    except TemplateDoesNotExist:
        pass

    # 2) بديل منطقي من مدير الثيمات (إن وُجد)
    try:
        get_template('theme_manager/overview.html')
        return render(request, 'theme_manager/overview.html', {})
    except TemplateDoesNotExist:
        pass

    # 3) سقوط آمن إلى صفحات النظام الثابتة
    try:
        return redirect('core:overview')
    except Exception:
        return redirect('core:launcher')


from django.shortcuts import render

def index(request):
    return render(request, 'dark_mode/index.html')


def app_home(request):
    return render(request, 'apps/dark_mode/home.html', {'app': 'dark_mode'})

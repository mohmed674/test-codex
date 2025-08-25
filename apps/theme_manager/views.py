from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.contrib.auth.decorators import login_required

@login_required
def overview(request):
    """
    سقوط آمن:
      1) إن وُجد القالب theme_manager/overview.html نعرضه.
      2) وإلا نعرض core/overview.html مباشرة.
      3) ولو غير موجودة لأي سبب، نحول إلى core:overview ثم core:launcher.
    """
    try:
        get_template('theme_manager/overview.html')
        return render(request, 'theme_manager/overview.html', {})
    except TemplateDoesNotExist:
        pass

    try:
        get_template('core/overview.html')
        return render(request, 'core/overview.html', {})
    except TemplateDoesNotExist:
        pass

    try:
        return redirect('core:overview')
    except Exception:
        return redirect('core:launcher')


from django.shortcuts import render

def index(request):
    return render(request, 'theme_manager/index.html')


def app_home(request):
    return render(request, 'apps/theme_manager/home.html', {'app': 'theme_manager'})

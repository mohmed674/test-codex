# D:\ERP_CORE\clients\views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template.exceptions import TemplateDoesNotExist

from .models import Client
from .forms import ClientForm

# ✅ استيراد كسول/آمن لموديولات اختيارية حتى لا تكسر التحميل
try:
    # قد لا تكون weasyprint مثبتة في كل البيئات
    from weasyprint import HTML as _WeasyHTML  # type: ignore
except Exception:
    _WeasyHTML = None

try:
    # ملف الذكاء الاصطناعي قد لا يكون موجودًا دائمًا
    from .ai import get_ai_insight_for_client as _ai_insight  # type: ignore
except Exception:
    _ai_insight = None


def _html(title: str, body: str) -> HttpResponse:
    """عرض HTML بديل بسيط عند غياب القوالب."""
    return HttpResponse(
        f"""<!doctype html>
<html lang="ar" dir="rtl">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title></head>
<body style="font-family: system-ui, -apple-system, Segoe UI, Roboto; direction: rtl; padding: 16px">
{body}
</body></html>"""
    )


# ==================== CRUD ====================

@login_required
def client_list(request):
    clients = Client.objects.all()
    try:
        return render(request, 'clients/client_list.html', {'clients': clients})
    except TemplateDoesNotExist:
        rows = "".join(f"<li>{c.name}</li>" for c in clients[:100])
        return _html("قائمة العملاء (عرض بديل)", f"<h1>العملاء</h1><ol>{rows}</ol>")


@login_required
def client_create(request):
    form = ClientForm(request.POST or None)
    if form.is_valid():
        client = form.save()
        messages.success(request, f"✅ تم إضافة العميل {client.name} بنجاح.")
        return redirect('client_list')  # سيعمل مع urls الحالية؛ سنوحد التسمية لاحقًا
    try:
        return render(request, 'clients/client_form.html', {'form': form})
    except TemplateDoesNotExist:
        return _html("إضافة عميل (بديل)", "<p>القالب غير متوفر. أضف clients/client_form.html لاحقًا.</p>")


@login_required
def client_update(request, pk):
    client = get_object_or_404(Client, pk=pk)
    form = ClientForm(request.POST or None, instance=client)
    if form.is_valid():
        form.save()
        messages.success(request, f"✏️ تم تحديث بيانات العميل {client.name} بنجاح.")
        return redirect('client_list')
    try:
        return render(request, 'clients/client_form.html', {'form': form})
    except TemplateDoesNotExist:
        return _html("تعديل عميل (بديل)", "<p>القالب غير متوفر. أضف clients/client_form.html لاحقًا.</p>")


@login_required
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        name = client.name
        client.delete()
        messages.warning(request, f"🗑️ تم حذف العميل {name} بنجاح.")
        return redirect('client_list')
    try:
        return render(request, 'clients/client_confirm_delete.html', {'client': client})
    except TemplateDoesNotExist:
        return _html("حذف عميل (بديل)", f"<p>هل أنت متأكد من حذف {client.name}؟</p>")


# ==================== ذكاء اصطناعي / تقارير ====================

@login_required
def client_ai_insight(request, pk):
    client = get_object_or_404(Client, pk=pk)
    # احمِ العرض إذا كانت دالة الذكاء غير متوفرة
    insight = None
    try:
        if _ai_insight:
            insight = _ai_insight(client)
    except Exception:
        insight = None

    ctx = {'client': client, 'insight': insight or {"note": "لم تتوفر تحليلات AI في هذه البيئة."}}
    try:
        return render(request, 'clients/ai_insights.html', ctx)
    except TemplateDoesNotExist:
        return _html(
            "تحليل AI (بديل)",
            f"<h1>تحليل {client.name}</h1><pre>{ctx['insight']}</pre>"
        )


@login_required
def client_pdf_view(request, pk):
    client = get_object_or_404(Client, pk=pk)
    # إذا weasyprint متاحة، نُصدر PDF؛ غير ذلك نرجع HTML
    if _WeasyHTML:
        try:
            from django.template.loader import get_template  # استيراد محلي آمن
            template = get_template('clients/client_pdf.html')
            html = template.render({'client': client})
            pdf_file = _WeasyHTML(string=html).write_pdf()
            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'filename="client_{client.id}.pdf"'
            return response
        except TemplateDoesNotExist:
            return _html("PDF العميل (بديل)", f"<h1>{client.name}</h1><p>أضف القالب clients/client_pdf.html لاحقًا.</p>")
        except Exception:
            # أي خطأ في التوليد يرجع HTML بديل
            return _html("PDF العميل (بديل)", f"<h1>{client.name}</h1><p>تعذر توليد PDF في هذه البيئة.</p>")
    else:
        return _html("PDF العميل (بديل)", f"<h1>{client.name}</h1><p>weasyprint غير متاحة.</p>")


@login_required
def client_analysis_dashboard(request):
    clients = Client.objects.all()
    active_clients = clients.filter(is_active=True).count()
    inactive_clients = clients.filter(is_active=False).count()
    ctx = {
        'clients': clients,
        'active_clients': active_clients,
        'inactive_clients': inactive_clients,
    }
    try:
        return render(request, 'clients/client_analysis_dashboard.html', ctx)
    except TemplateDoesNotExist:
        body = f"""
<h1>لوحة تحليل العملاء (بديل)</h1>
<ul>
  <li>العملاء النشطون: <strong>{active_clients}</strong></li>
  <li>العملاء غير النشطين: <strong>{inactive_clients}</strong></li>
</ul>
"""
        return _html("لوحة تحليل العملاء", body)


from django.shortcuts import render

def index(request):
    return render(request, 'clients/index.html')


def app_home(request):
    return render(request, 'apps/clients/home.html', {'app': 'clients'})

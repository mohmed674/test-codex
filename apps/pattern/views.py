# ERP_CORE/pattern/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import PatternDesign, PatternPiece, PatternExecution
from .forms import PatternDesignForm, PatternPieceForm, PatternExecutionForm
from django.contrib.auth.decorators import login_required
from core.utils import render_to_pdf, export_to_excel
from django.utils import timezone

# ✅ لوحة التحكم

@login_required
def pattern_dashboard(request):
    total_designs = PatternDesign.objects.count()
    total_executions = PatternExecution.objects.count()
    return render(request, 'pattern/dashboard.html', {
        'total_designs': total_designs,
        'total_executions': total_executions,
    })


# ✅ عرض التصاميم

@login_required
def design_list_view(request):
    designs = PatternDesign.objects.all()

    if request.GET.get("download_pdf") == "1":
        return render_to_pdf("pattern/designs_pdf.html", {"designs": designs, "request": request})

    if request.GET.get("export") == "1":
        data = [{
            "العنوان": d.title,
            "التصنيف": d.category,
            "الوصف": d.description,
            "التاريخ": d.created_at.strftime("%Y-%m-%d"),
        } for d in designs]
        return export_to_excel(data, filename="pattern_designs.xlsx")

    return render(request, 'pattern/design_list.html', {'designs': designs})


# ✅ إضافة تصميم

@login_required
def design_create_view(request):
    if request.method == 'POST':
        form = PatternDesignForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = request.user
            obj.save()
            return redirect('pattern:design_list')
    else:
        form = PatternDesignForm()
    return render(request, 'pattern/design_form.html', {'form': form})


# ✅ إدارة القطع

@login_required
def piece_list_view(request, design_id):
    design = get_object_or_404(PatternDesign, id=design_id)
    pieces = PatternPiece.objects.filter(design=design)
    return render(request, 'pattern/piece_list.html', {'design': design, 'pieces': pieces})


@login_required
def piece_create_view(request, design_id):
    design = get_object_or_404(PatternDesign, id=design_id)
    if request.method == 'POST':
        form = PatternPieceForm(request.POST)
        if form.is_valid():
            piece = form.save(commit=False)
            piece.design = design
            piece.save()
            return redirect('pattern:piece_list', design_id=design.id)
    else:
        form = PatternPieceForm()
    return render(request, 'pattern/piece_form.html', {'form': form, 'design': design})


# ✅ تنفيذ باترون

@login_required
def execution_list_view(request):
    executions = PatternExecution.objects.select_related('design', 'executed_by', 'production_order')

    if request.GET.get("download_pdf") == "1":
        return render_to_pdf("pattern/executions_pdf.html", {"executions": executions, "request": request})

    if request.GET.get("export") == "1":
        data = [{
            "الباترون": e.design.title,
            "نوع التنفيذ": e.execution_type,
            "أمر الإنتاج": e.production_order.order_number if e.production_order else "",
            "المنفذ": str(e.executed_by),
            "التاريخ": e.executed_at.strftime("%Y-%m-%d %H:%M"),
        } for e in executions]
        return export_to_excel(data, filename="pattern_executions.xlsx")

    return render(request, 'pattern/execution_list.html', {'executions': executions})


@login_required
def execution_create_view(request):
    if request.method == 'POST':
        form = PatternExecutionForm(request.POST)
        if form.is_valid():
            execution = form.save(commit=False)
            execution.executed_by = request.user
            execution.executed_at = timezone.now()
            execution.save()
            return redirect('pattern:execution_list')
    else:
        form = PatternExecutionForm()
    return render(request, 'pattern/execution_form.html', {'form': form})


from django.shortcuts import render

def index(request):
    return render(request, 'pattern/index.html')


def app_home(request):
    return render(request, 'apps/pattern/home.html', {'app': 'pattern'})

from django.shortcuts import render, redirect
from .models import Evaluation
from .forms import EvaluationForm
from core.utils import render_to_pdf, export_to_excel

def evaluation_list(request):
    evaluations = Evaluation.objects.select_related('employee').all()

    if request.GET.get("download_pdf"):
        return render_to_pdf("evaluation/evaluation_pdf.html", {"evaluations": evaluations, "request": request})

    if request.GET.get("export") == "1":
        data = [{
            "الموظف": e.employee.name,
            "التاريخ": e.date.strftime("%Y-%m-%d"),
            "الانضباط": e.attendance_score,
            "الإنتاج": e.productivity_score,
            "السلوك": e.behavior_score,
            "النهائي": e.final_score
        } for e in evaluations]
        return export_to_excel(data, "evaluation_report.xlsx")

    return render(request, "evaluation/evaluation_list.html", {"evaluations": evaluations})


def evaluation_create(request):
    form = EvaluationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("evaluation:list")
    return render(request, "evaluation/evaluation_form.html", {"form": form})


from django.shortcuts import render

def index(request):
    return render(request, 'evaluation/index.html')


def app_home(request):
    return render(request, 'apps/evaluation/home.html', {'app': 'evaluation'})

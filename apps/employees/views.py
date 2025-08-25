from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy, reverse, NoReverseMatch
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string, get_template
from django.template import TemplateDoesNotExist
from django.contrib.auth import get_user_model
from django.apps import apps  # ✅ جديد

from datetime import datetime, date
import openpyxl
from weasyprint import HTML

from apps.employees.models import Employee, MonthlyIncentive, AttendanceRecord
from apps.production.models import ProductionLog
from apps.work_regulations.models import EmployeeAgreement, Regulation
from apps.payroll.models import Salary
from apps.employees.forms import EmployeeForm
from apps.employees.utils.logic import calculate_employee_rewards, calculate_final_salary


# ===== Helpers =====
def _model_fields(model):
    return {f.name for f in model._meta.get_fields()}

def _pick(names, candidates, default=None):
    s = set(names)
    for c in candidates:
        if c in s:
            return c
    return default

def _emp_name_field():
    return _pick(_model_fields(Employee),
                 ("name", "full_name", "display_name", "username", "first_name", "code"),
                 default="id")

def _find_fk_to(model, target_model, fallbacks=("employee", "user")):
    for f in model._meta.get_fields():
        if getattr(f, "is_relation", False) and getattr(f, "many_to_one", False):
            try:
                if f.remote_field and f.remote_field.model is target_model:
                    return f.name
            except Exception:
                pass
    return _pick(_model_fields(model), fallbacks)

def _find_date_field(model):
    return _pick(_model_fields(model),
                 ("date", "created_at", "timestamp", "day", "happened_at", "occurred_at"))

def _reverse_or_fallback(names, *args, **kwargs):
    for n in names:
        try:
            return reverse(n, *args, **kwargs)
        except NoReverseMatch:
            continue
    return "/"


# ===== Views =====
class EmployeeListView(ListView):
    model = Employee
    template_name = 'employees/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 25

    def get_ordering(self):
        name_f = _emp_name_field()
        return [name_f]

    def get_queryset(self):
        queryset = super().get_queryset()
        q = (self.request.GET.get('search') or self.request.GET.get('q') or '').strip()
        if q:
            name_f = _emp_name_field()
            queryset = queryset.filter(**{f"{name_f}__icontains": q})
        return queryset


class EmployeeCreateView(CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employees/employee_form.html'
    success_url = reverse_lazy('employees:employee_list')

    def get_template_names(self):
        candidates = [
            'employees/employee_form.html',
            'employees/form.html',
            'core/employee_form.html',
            'core/form.html',
        ]
        for tpl in candidates:
            try:
                get_template(tpl)
                return [tpl]
            except TemplateDoesNotExist:
                continue
        return [self.template_name]

    def get_success_url(self):
        return _reverse_or_fallback(('employees:employee_list', 'employee_list', 'core:overview'))

    def form_valid(self, form):
        messages.success(self.request, "✅ تم إضافة الموظف بنجاح")
        return super().form_valid(form)


class EmployeeUpdateView(UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employees/employee_form.html'
    success_url = reverse_lazy('employees:employee_list')

    def get_template_names(self):
        candidates = [
            'employees/employee_form.html',
            'employees/form.html',
            'core/employee_form.html',
            'core/form.html',
        ]
        for tpl in candidates:
            try:
                get_template(tpl)
                return [tpl]
            except TemplateDoesNotExist:
                continue
        return [self.template_name]

    def get_success_url(self):
        return _reverse_or_fallback(('employees:employee_list', 'employee_list', 'core:overview'))

    def form_valid(self, form):
        messages.success(self.request, "✅ تم تحديث بيانات الموظف بنجاح")
        return super().form_valid(form)


def employee_profile(request, pk):
    emp = get_object_or_404(Employee, pk=pk)

    # ✅ استيراد ديناميكي للنموذج
    DisciplineRecord = apps.get_model("discipline", "DisciplineRecord")

    disc_emp_fk = _find_fk_to(DisciplineRecord, Employee, fallbacks=("employee", "emp", "worker"))
    disc_date_f = _find_date_field(DisciplineRecord) or "date"
    records = DisciplineRecord.objects.all()
    if disc_emp_fk:
        records = records.filter(**{disc_emp_fk: emp})
    if disc_date_f:
        records = records.order_by(f"-{disc_date_f}")

    action_type = (request.GET.get('action_type') or '').strip()
    date_from = (request.GET.get('date_from') or '').strip()
    date_to   = (request.GET.get('date_to') or '').strip()

    if action_type and 'type' in _model_fields(DisciplineRecord):
        records = records.filter(type=action_type)
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            records = records.filter(**{f"{disc_date_f}__gte": from_date})
        except Exception:
            pass
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            records = records.filter(**{f"{disc_date_f}__lte": to_date})
        except Exception:
            pass

    prod_emp_fk = _find_fk_to(ProductionLog, Employee, fallbacks=("employee", "emp"))
    prod_date_f = _find_date_field(ProductionLog) or "date"
    production_logs = ProductionLog.objects.all()
    if prod_emp_fk:
        production_logs = production_logs.filter(**{prod_emp_fk: emp})
    if prod_date_f:
        production_logs = production_logs.order_by(f"-{prod_date_f}")

    for prod in production_logs:
        qty = 0
        wage = 0
        for qf in ("quantity", "qty", "count", "units"):
            if hasattr(prod, qf) and getattr(prod, qf) is not None:
                qty = getattr(prod, qf)
                break
        for wf in ("unit_wage", "wage", "unit_price", "rate"):
            if hasattr(prod, wf) and getattr(prod, wf) is not None:
                wage = getattr(prod, wf)
                break
        prod.total = (qty or 0) * (wage or 0)

    try:
        reg_date_f = _find_date_field(Regulation) or "created_at"
        regulation = Regulation.objects.latest(reg_date_f)
    except Exception:
        regulation = None

    regulation_status = None
    if regulation:
        User = get_user_model()
        fk_emp = _find_fk_to(EmployeeAgreement, Employee, fallbacks=("employee",))
        fk_user = _find_fk_to(EmployeeAgreement, User, fallbacks=("user",))
        q = Q(regulation=regulation)
        if fk_emp:
            q &= Q(**{fk_emp: emp})
        elif fk_user and hasattr(emp, "user") and getattr(emp, "user"):
            q &= Q(**{fk_user: emp.user})
        regulation_status = EmployeeAgreement.objects.filter(q).first()

    first_of_month = date.today().replace(day=1)
    incentive = MonthlyIncentive.objects.filter(employee=emp, month=first_of_month).first() \
        if "employee" in _model_fields(MonthlyIncentive) and "month" in _model_fields(MonthlyIncentive) else None

    if request.GET.get('export') == '1':
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Discipline Records"
        ws.append(['نوع الإجراء', 'القيمة', 'السبب', 'أنشئ بواسطة', 'التاريخ'])
        for r in records:
            r_type = getattr(r, 'type', '-')
            r_value = getattr(r, 'value', None)
            r_reason = getattr(r, 'reason', '-') if hasattr(r, 'reason') else '-'
            r_created_by = getattr(r, 'created_by', '-') if hasattr(r, 'created_by') else '-'
            r_date_val = getattr(r, disc_date_f, None)
            r_date = r_date_val.strftime('%Y-%m-%d') if hasattr(r_date_val, 'strftime') else str(r_date_val or '-')
            ws.append([r_type, str(r_value) if r_value is not None else '-', r_reason, str(r_created_by), r_date])
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        safe_name = getattr(emp, _emp_name_field(), f"emp_{emp.pk}")
        response['Content-Disposition'] = f'attachment; filename=discipline_{safe_name}.xlsx'
        wb.save(response)
        return response

    if request.GET.get('download_pdf') == '1':
        context = {
            'employee': emp,
            'records': records,
            'production_logs': production_logs,
            'regulation_status': regulation_status,
            'incentive': incentive,
            'request': request,
        }
        try:
            html_string = render_to_string('employees/employee_discipline_pdf.html', context)
        except TemplateDoesNotExist:
            rows = ''.join(
                f"<tr><td>{getattr(r, 'type', '')}</td>"
                f"<td>{getattr(r, 'value', '')}</td>"
                f"<td>{getattr(r, 'reason', '')}</td>"
                f"<td>{getattr(r, 'created_by', '')}</td>"
                f"<td>{getattr(r, disc_date_f, '')}</td></tr>"
                for r in records
            )
            html_string = f"""
            <html><head><meta charset="utf-8"><style>
            body{{font-family:DejaVu Sans, Arial;}} table{{width:100%;border-collapse:collapse}}
            th,td{{border:1px solid #999;padding:6px;font-size:12px;text-align:center}}
            </style></head><body>
            <h3>Employee Discipline</h3>
            <table>
              <thead><tr><th>نوع الإجراء</th><th>القيمة</th><th>السبب</th><th>أنشئ بواسطة</th><th>التاريخ</th></tr></thead>
              <tbody>{rows}</tbody>
            </table>
            </body></html>
            """
        html = HTML(string=html_string)
        pdf_file = html.write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        safe_name = getattr(emp, _emp_name_field(), f"emp_{emp.pk}")
        response['Content-Disposition'] = f'inline; filename=discipline_{safe_name}.pdf'
        return response

    return render(request, 'employees/employee_profile.html', {
        'employee': emp,
        'records': records,
        'production_logs': production_logs,
        'regulation_status': regulation_status,
        'incentive': incentive,
        'request': request,
    })


def calculate_all_salaries(request):
    employees = Employee.objects.all()
    month = timezone.now().replace(day=1)
    for emp in employees:
        calculate_employee_rewards(emp, month)
        final = calculate_final_salary(emp, month)
        Salary.objects.update_or_create(
            employee=emp,
            month=month,
            defaults={'amount': final}
        )
    messages.success(request, "تم احتساب المرتبات تلقائيًا حسب اللائحة")
    try:
        return redirect('payroll:salary_list')
    except NoReverseMatch:
        return redirect(_reverse_or_fallback(('employees:employee_list', 'employee_list', 'core:overview')))


def index(request):
    return render(request, 'employees/index.html')


def app_home(request):
    return render(request, 'apps/employees/home.html', {'app': 'employees'})

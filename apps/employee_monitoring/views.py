from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Count, Q
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.http import HttpResponse
from weasyprint import HTML
from core.utils import export_to_excel

from .forms import MonitoringForm
from .models import MonitoringRecord
from apps.attendance.models import Attendance
from apps.discipline.models import DisciplineRecord
from apps.payroll.models import Salary
from apps.employees.models import Employee


# ===== Helpers (تكيّف تلقائي مع أسماء الحقول/العلاقات) =====
def _field_names(model):
    return {f.name for f in model._meta.get_fields()}

def _find_emp_fk(model):
    # ابحث عن أقرب FK يشير إلى Employee
    for f in model._meta.get_fields():
        if getattr(f, "is_relation", False) and getattr(f, "many_to_one", False):
            try:
                if f.remote_field and f.remote_field.model is Employee:
                    return f.name
            except Exception:
                pass
    # تخمينات احتياطية
    for name in ("employee", "emp", "worker", "staff", "user"):
        if name in _field_names(model):
            return name
    return None

def _find_date_field(model):
    # ابحث عن حقل تاريخ/تاريخ-وقت شائع
    candidates = ("date", "created_at", "timestamp", "happened_at", "occurred_at", "day")
    names = _field_names(model)
    for n in candidates:
        if n in names:
            return n
    return None

def _emp_name_path():
    # اختر حقلاً نصيًا للاسم داخل Employee
    names = _field_names(Employee)
    for n in ("name", "full_name", "display_name", "username", "first_name"):
        if n in names:
            return n
    return "id"


# 🔧 إدخال يدوي لمراقبة خاصة
def monitoring_input(request):
    if request.method == 'POST':
        form = MonitoringForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employee_monitoring:monitoring_dashboard')
    else:
        form = MonitoringForm()
    return render(request, 'employee_monitoring/input.html', {'form': form})


# بناء سياق اللوحة (لا يعتمد على TemplateResponse.context_data)
def _build_dashboard_context():
    today = timezone.now().date()

    records = MonitoringRecord.objects.all().order_by('-date') if 'date' in _field_names(MonitoringRecord) else MonitoringRecord.objects.all()

    alerts = []

    # إعدادات ديناميكية للحضور والانضباط
    att_emp_fk = _find_emp_fk(Attendance)
    att_date_f = _find_date_field(Attendance)
    disc_emp_fk = _find_emp_fk(DisciplineRecord)
    disc_date_f = _find_date_field(DisciplineRecord)

    emp_name_field = _emp_name_path()

    # غياب متكرر (>=3 خلال الشهر)
    try:
        if att_emp_fk and att_date_f and 'status' in _field_names(Attendance):
            att_abs_qs = Attendance.objects.filter(**{f'{att_date_f}__month': today.month}, status='absent')
            key = f'{att_emp_fk}__{emp_name_field}'
            for r in att_abs_qs.values(key).annotate(total=Count('id')).filter(total__gte=3):
                emp_label = r.get(key)
                alerts.append(f"🔴 الموظف {emp_label} غاب {r['total']} مرة هذا الشهر.")
    except Exception:
        pass

    # تلاعب محتمل بالبصمة (تأخير أو خروج مفقود >=5)
    try:
        has_exit = 'exit_time' in _field_names(Attendance)
        if att_emp_fk and att_date_f:
            filt = {f'{att_date_f}__month': today.month}
            qs = Attendance.objects.filter(**filt)
            if 'status' in _field_names(Attendance):
                qs = qs.filter(Q(status='late') | (Q(exit_time=None) if has_exit else Q()))
            key = f'{att_emp_fk}__{emp_name_field}'
            for m in qs.values(key).annotate(total=Count('id')).filter(total__gte=5):
                emp_label = m.get(key)
                alerts.append(f"⚠️ احتمال تلاعب: {emp_label} لديه {m['total']} حضور مشبوه.")
    except Exception:
        pass

    # موظفون بلا أي حضور هذا الشهر
    try:
        if att_emp_fk and att_date_f:
            present_ids = Attendance.objects.filter(**{f'{att_date_f}__month': today.month}).values_list(att_emp_fk, flat=True)
            inactive = Employee.objects.exclude(id__in=list(present_ids))
            for i in inactive:
                name_val = getattr(i, emp_name_field, None) or getattr(i, 'get_full_name', lambda: str(i))()
                alerts.append(f"🟠 الموظف {name_val} لم يسجل أي حضور هذا الشهر.")
    except Exception:
        pass

    # التصنيفات الذكية
    classifications = []
    for emp in Employee.objects.all():
        # غياب
        try:
            absences = 0
            if att_emp_fk and att_date_f and 'status' in _field_names(Attendance):
                absences = Attendance.objects.filter(**{
                    att_emp_fk: emp.id,
                    f'{att_date_f}__month': today.month,
                    'status': 'absent'
                }).count()
        except Exception:
            absences = 0

        # تأخير
        try:
            late = 0
            if att_emp_fk and att_date_f and 'status' in _field_names(Attendance):
                late = Attendance.objects.filter(**{
                    att_emp_fk: emp.id,
                    f'{att_date_f}__month': today.month,
                    'status': 'late'
                }).count()
        except Exception:
            late = 0

        # مخالفات
        try:
            discipline_cnt = 0
            if disc_emp_fk and disc_date_f:
                discipline_cnt = DisciplineRecord.objects.filter(**{
                    disc_emp_fk: emp.id,
                    f'{disc_date_f}__month': today.month
                }).count()
        except Exception:
            discipline_cnt = 0

        # مرتب
        try:
            salary_val = '-'
            s_fields = _field_names(Salary)
            sal = None
            if 'month' in s_fields:
                sal = Salary.objects.filter(employee=emp, month=today.month).first() if 'employee' in s_fields else Salary.objects.filter(month=today.month).first()
            else:
                s_date_f = _find_date_field(Salary)
                if s_date_f:
                    sal = Salary.objects.filter(**{s_date_f + '__month': today.month}).first()
            if sal:
                for amt in ('amount', 'net_amount', 'value', 'total', 'total_amount'):
                    if hasattr(sal, amt):
                        salary_val = getattr(sal, amt)
                        break
                else:
                    salary_val = str(sal)
        except Exception:
            salary_val = '-'

        if absences >= 3 or discipline_cnt >= 4:
            status = '⚠️ تحت المراجعة'
        elif absences == 0 and late <= 1:
            status = '✅ ملتزم'
        else:
            status = '🟡 مستقر'

        classifications.append({
            'employee': emp,
            'absences': absences,
            'late': late,
            'discipline': discipline_cnt,
            'salary': salary_val,
            'status': status
        })

    return {
        'records': records,
        'alerts': alerts,
        'classifications': classifications,
    }


# 🤖 لوحة المراقبة الذكية AI Monitor
def monitoring_dashboard(request):
    context = _build_dashboard_context()
    return render(request, 'employee_monitoring/dashboard.html', context)


# 🖨️ PDF Report
def monitoring_report_pdf(request):
    context = _build_dashboard_context()
    try:
        tpl = get_template('employee_monitoring/monitoring_pdf.html')
        html = tpl.render(context)
    except TemplateDoesNotExist:
        # قالب بديل مبسط عند عدم توفر القالب الأصلي
        rows = ''.join(
            f"<tr><td>{getattr(c['employee'], _emp_name_path(), c['employee'])}</td>"
            f"<td>{c['absences']}</td><td>{c['late']}</td>"
            f"<td>{c['discipline']}</td><td>{c['salary']}</td><td>{c['status']}</td></tr>"
            for c in context.get('classifications', [])
        )
        html = f"""
        <html><head><meta charset="utf-8"><style>
        body{{font-family:DejaVu Sans, Arial;}} table{{width:100%;border-collapse:collapse}}
        th,td{{border:1px solid #999;padding:6px;font-size:12px;text-align:center}}
        </style></head><body>
        <h3>AI Monitor Report</h3>
        <table>
          <thead><tr><th>الموظف</th><th>الغياب</th><th>التأخير</th><th>مخالفات</th><th>المرتب</th><th>التصنيف</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
        </body></html>
        """
    pdf_file = HTML(string=html).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="ai_monitor_report.pdf"'
    return response


# 📊 Excel Report
def monitoring_report_excel(request):
    context = _build_dashboard_context()
    data = []
    name_field = _emp_name_path()
    for c in context.get('classifications', []):
        emp = c['employee']
        emp_name = getattr(emp, name_field, None) or getattr(emp, 'get_full_name', lambda: str(emp))()
        data.append({
            'الموظف': emp_name,
            'الغياب': c['absences'],
            'التأخير': c['late'],
            'مخالفات': c['discipline'],
            'المرتب': c['salary'],
            'التصنيف': c['status'],
        })
    return export_to_excel(data, filename='ai_monitor_report.xlsx')


from django.shortcuts import render

def index(request):
    return render(request, 'employee_monitoring/index.html')


def app_home(request):
    return render(request, 'apps/employee_monitoring/home.html', {'app': 'employee_monitoring'})

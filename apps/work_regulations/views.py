from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse, NoReverseMatch
from django.utils import timezone

from .models import Regulation, EmployeeAgreement
from apps.employees.models import Employee


# ===== Helpers =====
def _model_fields(model):
    return {f.name for f in model._meta.get_fields()}

def _get_employee_for(user):
    # حاول الوصول عبر علاقة user.employee أو عبر FK في Employee
    if hasattr(user, "employee"):
        try:
            return user.employee
        except Exception:
            pass
    if "user" in _model_fields(Employee):
        try:
            return Employee.objects.filter(user=user).first()
        except Exception:
            return None
    return None

def _agreement_kwargs(employee, user, regulation):
    """
    يُرجع kwargs مناسبة للاستعلام/الإنشاء حسب ما إذا كان EmployeeAgreement مربوطًا بـ employee أو بـ user.
    """
    fields = _model_fields(EmployeeAgreement)
    data = {"regulation": regulation}
    if "employee" in fields and employee is not None:
        data["employee"] = employee
        return data
    if "user" in fields and user is not None:
        data["user"] = user
        return data
    # لا توجد حقول معروفة للربط
    return None

def _latest_regulation():
    fields = _model_fields(Regulation)
    for dt in ("created_at", "timestamp", "updated_at", "date", "published_at"):
        if dt in fields:
            try:
                return Regulation.objects.latest(dt)
            except Exception:
                pass
    return Regulation.objects.first()

def _safe_redirect(names):
    for n in names:
        try:
            return redirect(n)
        except NoReverseMatch:
            continue
    return redirect("/")


# ✅ عرض اللائحة الرسمية (مع سقوط آمن)
@login_required
def view_work_regulation(request):
    user = request.user
    employee = _get_employee_for(user)
    regulation = _latest_regulation()

    already_signed = False
    can_sign = False
    if regulation:
        kw = _agreement_kwargs(employee, user, regulation)
        if kw:
            already_signed = EmployeeAgreement.objects.filter(**kw).exists()
            can_sign = not already_signed and (employee is not None or "user" in _model_fields(EmployeeAgreement))

    if request.method == 'POST' and regulation and can_sign:
        kw = _agreement_kwargs(employee, user, regulation)
        if kw:
            obj, created = EmployeeAgreement.objects.get_or_create(**kw)
            if created or getattr(obj, "agreed_at", None) in (None, ""):
                # اضبط تاريخ الموافقة إن لم يكن مضبوطًا
                if "agreed_at" in _model_fields(EmployeeAgreement):
                    obj.agreed_at = timezone.now()
                    obj.save()
        return _safe_redirect(('employees:employee_list', 'core:overview'))

    return render(request, 'work_regulations/view.html', {
        'regulation': regulation,
        'already_signed': already_signed,
        'can_sign': can_sign,
        'employee': employee,
    })


# ✅ تسجيل الموافقة من رابط خارجي أو زر
@login_required
def agree_to_regulation(request, regulation_id):
    user = request.user
    employee = _get_employee_for(user)
    regulation = get_object_or_404(Regulation, id=regulation_id)

    kw = _agreement_kwargs(employee, user, regulation)
    if kw:
        obj, created = EmployeeAgreement.objects.get_or_create(**kw)
        if created or getattr(obj, "agreed_at", None) in (None, ""):
            if "agreed_at" in _model_fields(EmployeeAgreement):
                obj.agreed_at = timezone.now()
                obj.save()

    return _safe_redirect(('employees:employee_list', 'core:overview'))


from django.shortcuts import render

def index(request):
    return render(request, 'work_regulations/index.html')


def app_home(request):
    return render(request, 'apps/work_regulations/home.html', {'app': 'work_regulations'})

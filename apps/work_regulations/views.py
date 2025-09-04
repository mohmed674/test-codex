from __future__ import annotations

from typing import Any, Dict, Optional, Set

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import NoReverseMatch
from django.utils import timezone

from apps.employees.models import Employee

from .models import EmployeeAgreement, Regulation


# ===== Helpers =====
def _model_fields(model: type) -> Set[str]:
    return {f.name for f in model._meta.get_fields()}


def _get_employee_for(user: Any) -> Optional[Employee]:
    """
    حاول الوصول عبر علاقة user.employee أو عبر FK في Employee.
    يرجع None إن لم تتوفر العلاقة أو حدث خطأ.
    """
    if hasattr(user, "employee"):
        try:
            return user.employee  # type: ignore[attr-defined]
        except Exception:
            pass
    if "user" in _model_fields(Employee):
        try:
            return Employee.objects.filter(user=user).first()
        except Exception:
            return None
    return None


def _agreement_kwargs(
    employee: Optional[Employee], user: Any, regulation: Regulation
) -> Optional[Dict[str, Any]]:
    """
    يُرجع kwargs مناسبة للاستعلام/الإنشاء حسب ما إذا كان EmployeeAgreement
    مربوطًا بـ employee أو بـ user.
    """
    fields = _model_fields(EmployeeAgreement)
    data: Dict[str, Any] = {"regulation": regulation}
    if "employee" in fields and employee is not None:
        data["employee"] = employee
        return data
    if "user" in fields and user is not None:
        data["user"] = user
        return data
    # لا توجد حقول معروفة للربط
    return None


def _latest_regulation() -> Optional[Regulation]:
    fields = _model_fields(Regulation)
    for dt in ("created_at", "timestamp", "updated_at", "date", "published_at"):
        if dt in fields:
            try:
                return Regulation.objects.latest(dt)
            except Exception:
                pass
    return Regulation.objects.first()


def _safe_redirect(names: tuple[str, ...]) -> Any:
    for n in names:
        try:
            return redirect(n)
        except NoReverseMatch:
            continue
    return redirect("/")


# ✅ عرض اللائحة الرسمية (مع سقوط آمن)
@login_required
def view_work_regulation(request: Any) -> Any:
    user = request.user
    employee = _get_employee_for(user)
    regulation = _latest_regulation()

    already_signed = False
    can_sign = False
    if regulation:
        kw = _agreement_kwargs(employee, user, regulation)
        if kw:
            already_signed = EmployeeAgreement.objects.filter(**kw).exists()
            can_sign = not already_signed and (
                employee is not None or "user" in _model_fields(EmployeeAgreement)
            )

    if request.method == "POST" and regulation and can_sign:
        kw = _agreement_kwargs(employee, user, regulation)
        if kw:
            # Cast kwargs to appease static checkers; these are lookup fields, not 'defaults'
            kw_cast: Dict[str, Any] = dict(kw)
            obj, created = EmployeeAgreement.objects.get_or_create(**kw_cast)
            if created or getattr(obj, "agreed_at", None) in (None, ""):
                if "agreed_at" in _model_fields(EmployeeAgreement):
                    obj.agreed_at = timezone.now()
                    obj.save()
        return _safe_redirect(("employees:employee_list", "core:overview"))

    return render(
        request,
        "work_regulations/view.html",
        {
            "regulation": regulation,
            "already_signed": already_signed,
            "can_sign": can_sign,
            "employee": employee,
        },
    )


# ✅ تسجيل الموافقة من رابط خارجي أو زر
@login_required
def agree_to_regulation(request: Any, regulation_id: int) -> Any:
    user = request.user
    employee = _get_employee_for(user)
    regulation = get_object_or_404(Regulation, id=regulation_id)

    kw = _agreement_kwargs(employee, user, regulation)
    if kw:
        kw_cast: Dict[str, Any] = dict(kw)
        obj, created = EmployeeAgreement.objects.get_or_create(**kw_cast)
        if created or getattr(obj, "agreed_at", None) in (None, ""):
            if "agreed_at" in _model_fields(EmployeeAgreement):
                obj.agreed_at = timezone.now()
                obj.save()

    return _safe_redirect(("employees:employee_list", "core:overview"))


def index(request: Any) -> Any:
    return render(request, "work_regulations/index.html")


def app_home(request: Any) -> Any:
    return render(
        request, "apps/work_regulations/home.html", {"app": "work_regulations"}
    )

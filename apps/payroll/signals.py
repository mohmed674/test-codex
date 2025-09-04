# apps/payroll/signals.py
"""Payroll-related signals: raise AI/internal alerts on exceptional records.

- Uses existing models (Salary, PaymentRecord) to avoid import errors.
- Adds typing hints, unique dispatch_uids, and i18n.
- Guards optional relations with suppress to avoid hard failures.
"""

from __future__ import annotations

import logging
from contextlib import suppress
from typing import Any, Type

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from apps.ai_decision.models import AIDecisionAlert
from apps.internal_monitoring.alerts import trigger_risk_alert

from .models import PaymentRecord, Salary

logger = logging.getLogger(__name__)

# ===== Thresholds (tunable business rules) =====
DAILY_PAYMENT_ALERT = 1_000  # مبلغ يومي يعتبر غير اعتيادي
WEEKLY_PAYMENT_ALERT = 5_000  # مبلغ أسبوعي يعتبر غير اعتيادي
MONTHLY_PAYMENT_ALERT = 50_000  # مبلغ شهري يعتبر غير اعتيادي
DEDUCTIONS_RISK_RATIO = 0.5  # خصومات تتجاوز 50% من الراتب الأساسي تعتبر مخاطرة


# ✅ تنبيه عند تسجيل دفعة غير اعتيادية
@receiver(
    post_save,
    sender=PaymentRecord,
    dispatch_uid="payroll_notify_ai_on_payment_record",
)
def notify_ai_on_payment_record(
    sender: Type[PaymentRecord] | str,
    instance: PaymentRecord,
    created: bool,
    **kwargs: Any,
) -> None:
    """On new payment record, emit AI/internal alerts if amount is unusually high."""
    if not created:
        return

    amount = getattr(instance, "amount", 0)
    ptype = getattr(instance, "type", "")
    employee = getattr(instance, "employee", None)
    date_val = getattr(instance, "date", None)

    threshold = None
    if ptype == "daily":
        threshold = DAILY_PAYMENT_ALERT
    elif ptype == "weekly":
        threshold = WEEKLY_PAYMENT_ALERT
    elif ptype == "monthly":
        threshold = MONTHLY_PAYMENT_ALERT

    if threshold is not None and amount > threshold:
        msg = _("⚠️ %(emp)s سجل دفعة %(ptype)s بمبلغ %(amt)s في %(date)s") % {
            "emp": employee,
            "ptype": ptype,
            "amt": amount,
            "date": date_val,
        }
        AIDecisionAlert.objects.create(
            section="payroll",
            alert_type=_("دفعة غير اعتيادية"),
            message=msg,
            level="info",
        )


# ✅ تنبيه عند إنشاء راتب يحمل خصومات عالية أو صافي سالب
@receiver(
    post_save,
    sender=Salary,
    dispatch_uid="payroll_notify_ai_on_salary",
)
def notify_ai_on_salary(
    sender: Type[Salary] | str,
    instance: Salary,
    created: bool,
    **kwargs: Any,
) -> None:
    """On new salary, emit AI and/or risk alert if deductions are high or net is negative."""
    if not created:
        return

    base = getattr(instance, "base_salary", 0) or 0
    deductions = getattr(instance, "deductions", 0) or 0
    final_salary = getattr(instance, "final_salary", 0) or 0
    employee = getattr(instance, "employee", None)
    ym = f"{getattr(instance, 'month', '')}/{getattr(instance, 'year', '')}"

    # صافي راتب سالب → تنبيه تحذيري
    if final_salary < 0:
        msg = _("🔴 صافي راتب سلبي للموظف %(emp)s عن %(ym)s (صافي: %(net)s)") % {
            "emp": employee,
            "ym": ym,
            "net": final_salary,
        }
        AIDecisionAlert.objects.create(
            section="payroll",
            alert_type=_("صافي راتب سلبي"),
            message=msg,
            level="warning",
        )

    # خصومات مرتفعة جدًا نسبةً للراتب الأساسي → مخاطرة داخلية
    if base and deductions > base * DEDUCTIONS_RISK_RATIO:
        with suppress(Exception):  # employee.user قد لا يكون موجود
            trigger_risk_alert(
                event=_("خصومات مرتفعة"),
                user=getattr(employee, "user", None),
                risk_level="MEDIUM",
                note=_(
                    "خصومات %(ded)s تجاوزت %(pct)s%% من الأساسي %(base)s للموظف %(emp)s (%(ym)s)"
                )
                % {
                    "ded": deductions,
                    "pct": int(DEDUCTIONS_RISK_RATIO * 100),
                    "base": base,
                    "emp": employee,
                    "ym": ym,
                },
            )

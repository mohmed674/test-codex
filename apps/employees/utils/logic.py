# apps/employees/utils/logic.py
"""Business logic for employee rewards and final salary calculations.

- Decimal-safe computations for all monetary values.
- Strict typing to satisfy IDE/mypy (fixes red underlines on hour/minute/callables).
- Flake8-friendly formatting; no functional changes to thresholds or flow.
"""

from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Callable, Optional

from django.utils.timezone import now

from apps.employees.models import AttendanceRecord, Employee, MonthlyIncentive

# ===== Constants (tunable business rules) =====
START_OF_DAY_MINUTES = 9 * 60  # 9:00 AM
LATE_GRACE_MINUTES = 15  # minutes allowed beyond start time without penalty

PCT_ABSENCE_PROD = Decimal("0.15")  # 15% of daily production value
PCT_DELAY_PROD = Decimal("0.05")  # 5% of daily production value
PCT_RECUR_DELAY_PROD = Decimal("0.10")  # 10% of daily production value
PCT_RECUR_ABS_PROD = Decimal("0.20")  # 20% of daily production value

COMMITMENT_BONUS_PROD = Decimal("300")
COMMITMENT_BONUS_SAL = Decimal("500")
QUARTERLY_BONUS_PROD = Decimal("750")
QUARTERLY_BONUS_SAL = Decimal("1000")


def _to_decimal(value: float | int | Decimal | None) -> Decimal:
    """Coerce numbers to Decimal safely; None -> 0."""
    if isinstance(value, Decimal):
        return value
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def _hourly_rate(emp: Employee) -> Decimal:
    """Return hourly rate as Decimal."""
    rate_attr: float | Decimal | Callable[[], float | Decimal] | None = getattr(
        emp, "hourly_rate", 0
    )
    if callable(rate_attr):
        return _to_decimal(rate_attr())
    return _to_decimal(rate_attr)


def _daily_production_value(emp: Employee) -> Decimal:
    """Return daily production value as Decimal."""
    val_attr: float | Decimal | Callable[[], float | Decimal] | None = getattr(
        emp, "daily_production_value", 0
    )
    if callable(val_attr):
        return _to_decimal(val_attr())
    return _to_decimal(val_attr)


def _total_production_amount(emp: Employee, month: date) -> Decimal:
    """Return monthly production amount as Decimal."""
    fn: Optional[Callable[[date], float | Decimal]] = getattr(
        emp, "total_production_amount", None
    )
    if callable(fn):
        return _to_decimal(fn(month))
    return Decimal("0")


def calculate_employee_rewards(employee: Employee, month: date) -> None:
    """Compute and persist MonthlyIncentive for a given employee & month."""
    # سجلات الشهر
    records = AttendanceRecord.objects.filter(
        employee=employee, date__month=month.month, date__year=month.year
    )

    total_absences = 0
    delay_days: list[date] = []
    penalties = Decimal("0")

    for record in records:
        # غياب غير مُبرّر
        if getattr(record, "is_absent", False) and not getattr(
            record, "is_excused_absence", False
        ):
            total_absences += 1
            if getattr(employee, "is_production_based", False):
                penalties += PCT_ABSENCE_PROD * _daily_production_value(employee)
            else:
                penalties += _to_decimal(getattr(employee, "salary", 0)) / Decimal("30")

        # تأخير
        elif getattr(record, "check_in", None):
            check_in: Optional[datetime] = getattr(record, "check_in", None)
            if isinstance(check_in, datetime):
                check_in_minutes = check_in.hour * 60 + check_in.minute
                delay_minutes = max(0, check_in_minutes - START_OF_DAY_MINUTES)
                if delay_minutes > LATE_GRACE_MINUTES:
                    delay_days.append(record.date)
                    delay_hours = Decimal(delay_minutes) / Decimal("60")
                    if getattr(employee, "is_production_based", False):
                        penalties += PCT_DELAY_PROD * _daily_production_value(employee)
                    else:
                        penalties += (
                            delay_hours * Decimal("1.5") * _hourly_rate(employee)
                        )

    # خصم إضافي بسبب تكرار التأخير >= 3 مرات لليوم نفسه
    delay_counter = Counter(delay_days)
    for _day, count in delay_counter.items():
        if count >= 3:
            if getattr(employee, "is_production_based", False):
                penalties += PCT_RECUR_DELAY_PROD * _daily_production_value(employee)
            else:
                penalties += _to_decimal(getattr(employee, "salary", 0)) / Decimal("30")

    # خصم بسبب الغياب المتكرر
    if total_absences > 2:
        if getattr(employee, "is_production_based", False):
            penalties += PCT_RECUR_ABS_PROD * _daily_production_value(employee)
        else:
            penalties += Decimal("2") * (
                _to_decimal(getattr(employee, "salary", 0)) / Decimal("30")
            )

    # مكافآت: انتظام كامل
    commitment_bonus = Decimal("0")
    quarterly_bonus = Decimal("0")
    if total_absences == 0 and len(delay_days) == 0:
        commitment_bonus = (
            COMMITMENT_BONUS_PROD
            if getattr(employee, "is_production_based", False)
            else COMMITMENT_BONUS_SAL
        )

        # مكافأة ربع سنوية (3 شهور بلا غياب)
        last_3_months_start = now().date().replace(day=1) - timedelta(days=90)
        full_clean = not AttendanceRecord.objects.filter(
            employee=employee, date__gte=last_3_months_start, is_absent=True
        ).exists()
        if full_clean:
            quarterly_bonus = (
                QUARTERLY_BONUS_PROD
                if getattr(employee, "is_production_based", False)
                else QUARTERLY_BONUS_SAL
            )

    # حفظ أو تحديث سجل الحوافز
    MonthlyIncentive.objects.update_or_create(
        employee=employee,
        month=month,
        defaults={
            "commitment_bonus": commitment_bonus.quantize(
                Decimal("1."), rounding=ROUND_HALF_UP
            ),
            "quarterly_bonus": quarterly_bonus.quantize(
                Decimal("1."), rounding=ROUND_HALF_UP
            ),
            "penalty_total": penalties.quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            ),
        },
    )


# ✅ دالة حساب المرتب النهائي بعد دمج الحوافز والخصومات
def calculate_final_salary(employee: Employee, month: date) -> Decimal:
    """
    حساب المرتب النهائي للموظف بعد دمج الحوافز والخصومات (Decimal).
    """
    if getattr(employee, "is_production_based", False):
        base_salary = _total_production_amount(employee, month)
    else:
        base_salary = _to_decimal(getattr(employee, "salary", 0))

    incentive: Optional[MonthlyIncentive] = MonthlyIncentive.objects.filter(
        employee=employee, month=month
    ).first()

    if not incentive:
        bonus = Decimal("0")
        penalty = Decimal("0")
    else:
        bonus = _to_decimal(getattr(incentive, "commitment_bonus", 0)) + _to_decimal(
            getattr(incentive, "quarterly_bonus", 0)
        )
        penalty = _to_decimal(getattr(incentive, "penalty_total", 0))

    final_salary = (base_salary + bonus - penalty).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    return final_salary

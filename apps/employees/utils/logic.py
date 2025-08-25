from collections import Counter
from datetime import timedelta
from django.utils.timezone import now
from apps.employees.models import AttendanceRecord, MonthlyIncentive
from apps.employees.models import Employee  # مكرر ولكن يُترك للوضوح في المشروع

def calculate_employee_rewards(employee, month):
    # تصفية سجلات الشهر
    records = AttendanceRecord.objects.filter(
        employee=employee,
        date__month=month.month,
        date__year=month.year
    )

    total_delays = 0
    total_absences = 0
    delay_days = []
    penalties = 0

    for record in records:
        if record.is_absent and not record.is_excused_absence:
            total_absences += 1
            if employee.is_production_based:
                penalties += 0.15 * employee.daily_production_value()
            else:
                penalties += employee.salary / 30
        elif record.check_in:
            check_in_minutes = record.check_in.hour * 60 + record.check_in.minute
            delay_minutes = max(0, check_in_minutes - 540)  # بعد 9:00 ص
            if delay_minutes > 15:
                delay_days.append(record.date)
                delay_hours = delay_minutes / 60
                if employee.is_production_based:
                    penalties += 0.05 * employee.daily_production_value()
                else:
                    penalties += delay_hours * 1.5 * employee.hourly_rate()

    # خصم إضافي بسبب تكرار التأخير أكثر من 3 مرات
    delay_counter = Counter(delay_days)
    for day, count in delay_counter.items():
        if count >= 3:
            if employee.is_production_based:
                penalties += 0.10 * employee.daily_production_value()
            else:
                penalties += employee.salary / 30

    # خصم بسبب الغياب المتكرر
    if total_absences > 2:
        if employee.is_production_based:
            penalties += 0.20 * employee.daily_production_value()
        else:
            penalties += 2 * (employee.salary / 30)

    # المكافآت: انتظام كامل في الشهر
    commitment_bonus = 0
    quarterly_bonus = 0
    if total_absences == 0 and len(delay_days) == 0:
        commitment_bonus = 300 if employee.is_production_based else 500

        # مكافأة ربع سنوية (3 شهور بلا غياب)
        last_3_months_start = now().date().replace(day=1) - timedelta(days=90)
        full_clean = not AttendanceRecord.objects.filter(
            employee=employee,
            date__gte=last_3_months_start,
            is_absent=True
        ).exists()
        if full_clean:
            quarterly_bonus = 750 if employee.is_production_based else 1000

    # حفظ أو تحديث سجل الحوافز
    MonthlyIncentive.objects.update_or_create(
        employee=employee,
        month=month,
        defaults={
            'commitment_bonus': commitment_bonus,
            'quarterly_bonus': quarterly_bonus,
            'penalty_total': penalties,
        }
    )


# ✅ دالة حساب المرتب النهائي بعد دمج الحوافز والخصومات
def calculate_final_salary(employee, month):
    """
    ✅ حساب المرتب النهائي للموظف بعد دمج الحوافز والخصومات

    - المرتب الأساسي:
        • راتب ثابت إن لم يكن على الإنتاج
        • أو ناتج الإنتاج الشهري إن كان على الإنتاج

    - الحوافز:
        • مكافأة الالتزام
        • المكافأة الربع سنوية

    - الخصومات:
        • جميع الخصومات المجدولة (مهام / سلوك)

    :param employee: كائن الموظف
    :param month: الشهر المطلوب بصيغة datetime.date أو datetime.datetime
    :return: قيمة المرتب النهائي بعد الدمج
    """
    base_salary = (
        employee.salary 
        if not employee.is_production_based 
        else employee.total_production_amount(month)
    )

    incentive = MonthlyIncentive.objects.filter(employee=employee, month=month).first()

    if not incentive:
        bonus = 0
        penalty = 0
    else:
        bonus = (incentive.commitment_bonus or 0) + (incentive.quarterly_bonus or 0)
        penalty = incentive.penalty_total or 0

    final_salary = base_salary + bonus - penalty
    return final_salary

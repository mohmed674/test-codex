from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Department
from .forms import DepartmentForm
from apps.ai_decision.models import AIDecisionAlert
from apps.internal_monitoring.models import RiskIncident, ReportLog
from django.utils.timezone import now

# 🔍 قائمة الأقسام
def department_list(request):
    departments = Department.objects.all().order_by('-created_at')

    # عرض ذكي بتنسيق SAP-style
    headers = ['الاسم', 'الوصف', 'تاريخ الإنشاء', 'نشط', 'إجراءات']
    rows = []
    for dept in departments:
        rows.append([
            dept.name,
            dept.description or "—",
            dept.created_at.strftime("%Y-%m-%d"),
            "✅" if dept.is_active else "❌",
            {
                'edit_url': f"/departments/edit/{dept.pk}/",
                'delete_url': f"/departments/delete/{dept.pk}/"
            }
        ])

    return render(request, 'departments/list.html', {
        'departments': departments,
        'headers': headers,
        'rows': rows
    })


# ➕ إنشاء قسم جديد
def create_department(request):
    form = DepartmentForm(request.POST or None)
    if form.is_valid():
        department = form.save()
        messages.success(request, "✅ تم إنشاء القسم بنجاح.")

        # 🔔 تنبيه فوري للذكاء الاصطناعي
        AIDecisionAlert.objects.create(
            section="departments",
            message=f"📥 تم إضافة قسم جديد: {department.name}",
            level="info",
            timestamp=now()
        )

        # 🧠 تسجيل مخالفة تنظيمية
        RiskIncident.objects.create(
            user=request.user if request.user.is_authenticated else None,
            category="System",
            event_type="إنشاء قسم جديد",
            risk_level="LOW",
            notes=f"إنشاء قسم: {department.name}",
            reported_at=now()
        )

        # 📝 سجل التقارير
        ReportLog.objects.create(
            model='Department',
            action='Create',
            ref=str(department.pk),
            notes=f"إضافة قسم جديد: {department.name}",
            timestamp=now()
        )

        return redirect('department_list')
    return render(request, 'departments/create.html', {'form': form})


# ✏️ تعديل قسم
def update_department(request, pk):
    department = get_object_or_404(Department, pk=pk)
    form = DepartmentForm(request.POST or None, instance=department)
    if form.is_valid():
        form.save()
        messages.success(request, "✏️ تم تعديل القسم بنجاح.")

        AIDecisionAlert.objects.create(
            section="departments",
            message=f"✏️ تم تعديل القسم: {department.name}",
            level="info",
            timestamp=now()
        )

        RiskIncident.objects.create(
            user=request.user if request.user.is_authenticated else None,
            category="System",
            event_type="تعديل قسم",
            risk_level="MEDIUM",
            notes=f"تعديل القسم: {department.name}",
            reported_at=now()
        )

        ReportLog.objects.create(
            model='Department',
            action='Update',
            ref=str(department.pk),
            notes=f"تعديل قسم: {department.name}",
            timestamp=now()
        )

        return redirect('department_list')
    return render(request, 'departments/edit.html', {'form': form, 'department': department})


# 🗑️ حذف قسم
def delete_department(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        department_name = department.name
        department_pk = department.pk
        department.delete()
        messages.warning(request, "🗑️ تم حذف القسم.")

        AIDecisionAlert.objects.create(
            section="departments",
            message=f"🗑️ تم حذف قسم: {department_name}",
            level="warning",
            timestamp=now()
        )

        RiskIncident.objects.create(
            user=request.user if request.user.is_authenticated else None,
            category="System",
            event_type="حذف قسم",
            risk_level="HIGH",
            notes=f"🚫 حذف القسم: {department_name}",
            reported_at=now()
        )

        ReportLog.objects.create(
            model='Department',
            action='Delete',
            ref=str(department_pk),
            notes=f"🗑️ تم حذف قسم: {department_name}",
            timestamp=now()
        )

        return redirect('department_list')
    return render(request, 'departments/delete.html', {'department': department})


from django.shortcuts import render

def index(request):
    return render(request, 'departments/index.html')


def app_home(request):
    return render(request, 'apps/departments/home.html', {'app': 'departments'})

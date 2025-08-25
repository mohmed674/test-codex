# 🕒 Attendance App - نظام تسجيل الحضور والانصراف

## 🎯 الهدف
تسجيل وتتبع حضور الموظفين وانصرافهم، مع توفير تقارير دقيقة قابلة للطباعة والتصدير، وتكامل مع تقييمات الأداء.

## 🧩 الموديل الأساسي
- `Attendance`:
  - `evaluation`: ربط بتقييم الموظف.
  - `date`: التاريخ.
  - `status`: حاضر / غائب / متأخر.
  - `__str__`: اسم الموظف + الحالة + التاريخ.

## 🛠️ الوظائف الأساسية
- تسجيل حضور يدوي (`attendance_create`)
- عرض قائمة الحضور مع فلترة وتصدير (`attendance_list`)
- طباعة تقرير مباشر (`attendance_print_view`)
- تقارير الغياب والتأخير (`lateness_absence_list`)
- تصدير PDF/Excel عبر `attendance_exports.py`

## 📦 التكاملات
- ربط مباشر مع:
  - `evaluation.Evaluation`
  - `employees.Employee`
  - `lateness_absence` من تقييمات الموظفين.

## 🤖 الذكاء الاصطناعي (قيد التوسيع)
- تنبيهات في الحضور تشير إلى:
  - غياب بدون إذن = خصم تلقائي.
  - تأخير = يؤثر في تقييم الانضباط.

## 📤 التصدير
- PDF باستخدام WeasyPrint
- Excel باستخدام OpenPyXL
- جميع المنطق محفوظ في: `attendance/exports/attendance_exports.py`

## 📁 الملفات الداعمة
- `attendance_print.html`
- `attendance_pdf.html`
- `lateness_absence_pdf.html`
- `lateness_absence_print.html`

## 🧪 الاختبارات
- ملف `tests.py` موجود كقالب جاهز للتوسعة.


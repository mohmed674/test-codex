# 🧠 core – الوحدة الذكية الأساسية لنظام ERP

هذا التطبيق يمثل "الوحدة الأساسية" التي تدير العناصر المحورية في نظام ERP مثل الوظائف، المعايير، الأدوار، المراحل، والتقييمات، مع دعم الذكاء الاصطناعي والمراقبة الذكية.

---

## ⚙️ المكونات الرئيسية

### 🔸 النماذج (Models)
- `JobTitle`: المسمى الوظيفي
- `Unit`: وحدة قياس
- `EvaluationCriteria`: معايير التقييم
- `ProductionStageType`: مراحل الإنتاج
- `RiskThreshold`: حدود الخطورة
- `DepartmentRole`: أدوار الأقسام

> *(تمت مراجعتها ضمن `models.py` – غير مرفقة هنا)*

---

## 🧩 الوظائف والتكاملات

| الملف | الوظيفة |
|-------|---------|
| `helpers.py` | استهلاك خامات، قيد التكاليف، تقييمات الموظفين، تنبيهات AI |
| `signals.py` | إنشاء تنبيه ذكي ومخالفة مراقبة عند تسجيل مستخدم جديد |
| `tasks.py` | مهمة مجدولة لتشغيل AI والتحقق من الإعدادات الأساسية |
| `middleware.py` | عرض تنبيهات ذكية عند وجود عجز مخزني أو نشاط مشبوه |
| `permissions.py` | تحديد صلاحية "مدير النواة" |
| `ai.py` | فحص وجود معايير تقييم ومراحل إنتاج وتحذير الذكاء الاصطناعي |

---

## 🔌 التكاملات

| الملف | الخدمة |
|-------|--------|
| `whatsapp.py` | إرسال رسائل عبر WhatsApp باستخدام Twilio |
| `signature.py` | إرسال مستندات للتوقيع عبر API |
| `payments.py` | تكامل الدفع مع فوري |

---

## 📤 التصدير والطباعة

| الملف | الوظيفة |
|-------|----------|
| `pdf_render.py` | توليد PDF عبر WeasyPrint و xhtml2pdf |
| `rendering.py` | تحويل قالب HTML إلى PDF |
| `export_excel.py` | تصدير البيانات و الفواتير إلى Excel أو CSV |
| `export_utils.py` | دعم إضافي لتصدير PDF / Excel |

---

## 🧠 الذكاء الاصطناعي والمراقبة

- يتم تنبيه AI عبر `AIDecisionLog` و `AIDecisionAlert`
- يتم تسجيل الحوادث الذكية في `RiskIncident`
- جميع التنبيهات مرئية للمستخدم داخل الـ UI

---

## 🧪 واجهات API

تم توفير ViewSets جاهزة للنماذج الأساسية:

| المسار | الوظيفة |
|--------|---------|
| `/api/job-titles/` | CRUD للمسميات الوظيفية |
| `/api/units/` | CRUD للوحدات |
| `/api/evaluation-criteria/` | CRUD لمعايير التقييم |
| `/api/stage-types/` | CRUD لمراحل الإنتاج |
| `/api/risk-thresholds/` | CRUD لحدود المخاطر |
| `/api/department-roles/` | CRUD لأدوار الأقسام |

---

## 🖥️ القوالب

تم تصميم قوالب Odoo-style لكل شاشة:

- `job_title_list.html`, `job_title_form.html`, `job_title_create.html`
- `department_role_list.html`, `department_role_create.html`
- `stage_type_list.html`, `stage_type_create.html`
- `unit_list.html`, `unit_create.html`
- `criteria_list.html`, `criteria_create.html`
- `risk_threshold_list.html`, `risk_threshold_create.html`
- `dashboard.html`, `admin_dashboard.html`
- عناصر مشتركة: `datatable_template.html`, `tabs_template.html`, `form_create.html`, `_table_list.html`

---

## 🧱 التمبلت تاغز (Template Tags)

- `form_filters.py`: فلاتر CSS + تلميحات ذكية
- `smart_hints.py`: تلميحات إدخال مخصصة حسب القسم والحقل

---

## 🔐 الصلاحيات

- تعتمد على Django Groups
- مجموعة "Core Managers" هي المسؤولة عن الوصول إلى هذا التطبيق

---

## ⏱️ المهام المجدولة

- `run_core_ai_checks`: تُفعل آليًا لتحذير الذكاء الاصطناعي من نقص الإعدادات

---

## 🧾 ملاحظات

- هذا التطبيق جزء مركزي من المنصة ولا يجب حذفه
- كل شاشة داعمة للطباعة والتصدير PDF/Excel
- يدعم RTL، الهاتف، الأجهزة اللوحية، والمزامنة السحابية


# قائمة القضايا

1. **احتمال تكرار label لتطبيق PLM**
   - الدليل: `config/settings.py` يحمّل `apps.plm.apps.PlmConfig` بينما ملف الإعداد لا يحدد `label` صريح في `apps/plm/apps.py`.
   - المواقع: `config/settings.py:34-35`، `apps/plm/apps.py:3-5`.
   - الحل: إضافة خاصية `label` فريدة داخل `PlmConfig` لتجنب تعارض أسماء التطبيقات.

2. **استيراد مفقود لتطبيق media**
   - الدليل: `config/urls.py:52` و`config/settings.py:63` يشيران إلى `apps.media` رغم عدم وجود مجلد `apps/media`.
   - الناتج: \`ModuleNotFoundError: apps.media\`.
   - الحل: إنشاء تطبيق `apps/media` أو إزالة الإشارات إليه من الإعدادات والروابط.

3. **فجوات في الترجمة (i18n)**
   - الدليل: القالب الأساسي `core/templates/core/base.html` لا يحتوي على `{% load i18n %}` كما أن النص العربي «لوحة Core» غير ملفوف بـ`{% trans %}`.
   - المواقع: `core/templates/core/base.html:1-3,18`.
   - الحل: تحميل مكتبة i18n وإحاطة النصوص بـ`{% trans %}` لضمان دعم اللغات.

4. **فجوة REST/API في موديول المبيعات**
   - الدليل: `apps/sales/views.py` يحتوي على واجهات عرض عديدة بينما لا يوجد ملف `serializers.py` في نفس التطبيق.
   - المواقع: `apps/sales/views.py:1-8`، مخرجات `ls apps/sales` تبين غياب الملف.
   - الحل: إنشاء `serializers.py` وربط الواجهات بنقاط نهاية API مناسبة.

5. **نماذج بدون تسجيل في لوحة الإدارة**
   - الدليل: ملف `apps/qms/models.py` يعرّف كلاس `MeasurementType` لكن لا يوجد تسجيل مقابل في `apps/qms/admin.py`.
   - المواقع: `apps/qms/models.py:31-33`.
   - الحل: التأكد من تسجيل النماذج الأساسية في `admin.py` أو تأكيد أنها ليست نماذج فعلية (TextChoices).

6. **غياب اختبارات لتطبيقات رئيسية**
   - الدليل: لا يوجد ملف اختبارات داخل مجلد `apps/inventory`.
   - المواقع: مخرجات `ls apps/inventory`.
   - الحل: إنشاء مجلد `tests/` أو ملفات `tests.py` لتغطية النماذج والواجهات.

7. **تعليقات TODO غير معالجة**
   - الدليل: `apps/campaigns/integrations.py:19 و28` تحتوي على TODO لربط مزودي SMS/WhatsApp، و`apps/mobile/views.py:36` يحتوي على TODO لاستبدال بيانات ثابتة.
   - الحل: تنفيذ المهام المؤجلة أو توثيق خطة التنفيذ.

8. **اعتماديات ناقصة في requirements.txt**
   - الدليل: الملف `requirements.txt` يخلو من حزمتَي `django_celery_results` و`django-colorfield` رغم وجودهما في الإعدادات و`requirements_lock.txt`.
   - المواقع: `config/settings.py:44 و49`، `requirements_lock.txt:36`.
   - الحل: إضافة الحزم المفقودة إلى `requirements.txt` لتفادي أخطاء التثبيت.


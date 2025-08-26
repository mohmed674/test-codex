# خارطة طريق تطوير ذكية (Arabic-First)

## الأهداف
- جعل النظام عربيًا افتراضيًا مع تجربة مستقرة
- سد فجوات الوحدات الأساسية
- رفع الجودة (اختبارات/CI/أمان) للوصول لمستوى منتجات مثل Odoo/SAP

## Wave 1 (0–4 أسابيع)
- تهيئة البيئة: Docker + compose + Make targets
- إصلاح فشل pytest وتثبيت المتطلبات
- تمكين Arabic-First: RTL + locale/ar.* + اختيار اللغة بالإعدادات
- إنشاء CRUD كامل (API+Admin+Templates) للمحاسبة والمخزون
- CI/CD بسيط (GitHub Actions): black/isort/flake8 + pytest + safety
**KPI**: اختبارات تمر 100%، تغطية ≥ 60%، زمن إعداد بيئة < 10 دقائق

## Wave 2 (4–10 أسابيع)
- استكمال وحدات المبيعات/CRM وPOS والتكامل مع المخزون والفوترة
- تصميم لوحة PWA/React موحّدة بالعربية
- توحيد API (OpenAPI, versioning, error model) + API Gateway
- RBAC + Audit Log + سجلات عمليات
**KPI**: إقفال ≥ 70% من فجوات CRUD، زمن استجابة API P95 < 300ms

## Wave 3 (10–20 أسبوعًا)
- BI وتقارير متقدمة + تكامل مخزن بيانات خفيف
- إطلاق ML Pilot للطلب/الشذوذ المالي (استبدال mock)
- مراقبة كاملة (logs/metrics/traces) ونشر سحابي (K8s اختياري)
**KPI**: 2 نماذج ML في الإنتاج مع مراقبة، لوحات تقارير تنفيذية

## إدارة المخاطر
- Rollback عبر migrations محكومة و feature flags
- اختبارات عقدية للتكاملات

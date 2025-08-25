
## 🔸 ملف الفلتر العام الذكي: `ERP_CORE/core/templatetags/smart_hints.py`


from django import template

register = template.Library()

@register.simple_tag
def smart_hint(field_name, section):
    hints = {
        'accounting': {
            'debit_account': "✳️ اختر الحساب المناسب من دليل الحسابات...",
            'credit_account': "📤 الحساب الذي سيتم الإضافة إليه – مثال: البنك، النقدية...",
            'amount': "💰 أدخل المبلغ بالدقة – مثال: 2500.00",
            'description': "📝 اكتب وصفًا واضحًا للقيد مثل 'مرتبات يناير' أو 'سداد دفعة عميل'."
        },
        'attendance': {
            'status': "🕓 حدد الحالة بدقة – 'غياب بدون إذن' يؤدي إلى خصم وتنبيه الذكاء الاصطناعي."
        },
        'production': {
            'product_name': "✍️ أدخل الاسم كما هو مسجل في سجل المنتجات – سيتم ربطه تلقائيًا بالمخزون."
        },
        'employees': {
            'national_id': "📄 أدخل الرقم القومي بدقة (14 رقمًا) لتفادي تكرار السجلات."
        },
        'products': {
            'cost_price': "⚙️ يتم احتساب التكلفة تلقائيًا من الخامات وأوامر التشغيل – أدخل فقط إن أردت التعديل يدويًا."
        },
        # يمكن التوسعة بسهولة
    }
    return hints.get(section, {}).get(field_name, "")

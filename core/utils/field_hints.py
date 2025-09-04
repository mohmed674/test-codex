# core/utils/field_hints.py
from typing import Dict


def get_entry_hint(field_name: str, section: str) -> str:
    """
    يُرجع تلميحات ذكية للحقول حسب القسم.
    إذا لم يوجد تلميح يرجع نص فارغ.
    """
    hints: Dict[str, Dict[str, str]] = {
        "accounting": {
            "description": "📝 اكتب وصفًا واضحًا للقيد المحاسبي.",
            "amount": "💰 أدخل المبلغ بدقة مثل: 1500.00",
            "debit_account": "📥 الحساب الذي سيتم الخصم منه.",
            "credit_account": "📤 الحساب الذي سيتم الإضافة إليه.",
        },
        "attendance": {
            "status": "🕓 اختر الحالة مثل 'حضور'، 'غياب بإذن'، 'غياب بدون إذن'."
        },
        "sales": {
            "client": "👤 اختر العميل من قائمة العملاء المسجلين.",
            "total_amount": "💲 إجمالي قيمة الفاتورة قبل الخصم أو الضرائب.",
        },
        "inventory": {
            "product_code": "🔢 أدخل كود المنتج من الباركود أو النظام.",
            "quantity": "📦 الكمية بالوحدة المحددة (مثلاً: قطعة أو كرتونة).",
        },
    }
    return hints.get(section, {}).get(field_name, "")

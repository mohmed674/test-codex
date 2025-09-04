# apps/accounting/serializers.py
from decimal import Decimal
from typing import Any, Dict, Optional

from rest_framework import serializers

from .models import Customer, Invoice, JournalEntry, Payment, SupplierInvoice


class JournalEntrySerializer(serializers.ModelSerializer):
    # معلومات مساعدة للقراءة
    invoice_number = serializers.CharField(source="invoice.number", read_only=True)

    class Meta:
        model = JournalEntry
        fields = "__all__"
        read_only_fields = ("created_by",)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        قواعد أساسية:
        - ممنوع يكون المدين والدائن صفر معًا.
        - ممنوع يكون الإثنين > 0 في نفس الوقت (يفترض أحدهما فقط لكل قيد).
        """
        debit = attrs.get("debit", Decimal("0")) or Decimal("0")
        credit = attrs.get("credit", Decimal("0")) or Decimal("0")

        if (debit == 0 and credit == 0) or (debit > 0 and credit > 0):
            raise serializers.ValidationError(
                "يجب أن يكون إما مبلغ مدين أو مبلغ دائن فقط "
                "(ولا يمكن أن يكونا صفرًا معًا)."
            )
        return attrs

    def create(self, validated_data: Dict[str, Any]) -> JournalEntry:
        # ربط من قام بالإنشاء إن وُجد في السياق
        request = self.context.get("request")
        if request and hasattr(request.user, "employee"):
            validated_data["created_by"] = request.user.employee
        return super().create(validated_data)


class InvoiceSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = "__all__"

    def get_is_overdue(self, obj: Invoice) -> bool:
        try:
            return obj.is_overdue()
        except Exception:
            return False

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        date_issued = attrs.get(
            "date_issued",
            getattr(self.instance, "date_issued", None),
        )
        due_date = attrs.get("due_date", getattr(self.instance, "due_date", None))
        total_amount = attrs.get(
            "total_amount",
            getattr(self.instance, "total_amount", Decimal("0")),
        )

        if date_issued and due_date and due_date < date_issued:
            raise serializers.ValidationError(
                "تاريخ الاستحقاق يجب أن يكون بعد تاريخ الإصدار."
            )
        if total_amount is not None and Decimal(total_amount) < 0:
            raise serializers.ValidationError("إجمالي الفاتورة لا يمكن أن يكون سالبًا.")
        return attrs


class PaymentSerializer(serializers.ModelSerializer):
    invoice_number = serializers.CharField(source="invoice.number", read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"

    def validate_amount(self, value: Optional[Decimal]) -> Decimal:
        if value is None or value <= 0:
            raise serializers.ValidationError("مبلغ الدفعة يجب أن يكون أكبر من صفر.")
        return value


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"


# ✅ إدارة فواتير الموردين (API)
class SupplierInvoiceSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    payment_method_display = serializers.CharField(
        source="get_payment_method_display",
        read_only=True,
    )
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = SupplierInvoice
        fields = "__all__"

    def get_is_overdue(self, obj: SupplierInvoice) -> bool:
        try:
            return obj.is_overdue()
        except Exception:
            return False

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        date_issued = attrs.get(
            "date_issued",
            getattr(self.instance, "date_issued", None),
        )
        due_date = attrs.get("due_date", getattr(self.instance, "due_date", None))
        total_amount = attrs.get(
            "total_amount",
            getattr(self.instance, "total_amount", Decimal("0")),
        )

        if date_issued and due_date and due_date < date_issued:
            raise serializers.ValidationError(
                "تاريخ الاستحقاق يجب أن يكون بعد تاريخ الإصدار."
            )
        if total_amount is not None and Decimal(total_amount) < 0:
            raise serializers.ValidationError("إجمالي الفاتورة لا يمكن أن يكون سالبًا.")
        return attrs

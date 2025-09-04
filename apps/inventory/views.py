# apps/inventory/views.py
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

# ✅ المراقبة الذكية
from apps.internal_monitoring.alerts import trigger_risk_alert
from apps.internal_monitoring.models import RiskIncident
from apps.internal_monitoring.security import suspend_user_temporarily
# ✅ أدوات مساعدة
from core.utils import export_to_excel, render_to_pdf

from .forms import (InventoryItemForm, InventoryLocationForm,
                    InventoryTransactionForm)
# ✅ النماذج الحالية
from .models import (InventoryAudit, InventoryAuditItem, InventoryItem,
                     InventoryMovement, Warehouse)

# ----------------------- Helpers (typed & safe) -----------------------


def _safe(obj: Any, attr: str, default: Any = "") -> Any:
    return getattr(obj, attr, default)


def _choice_label(obj: Any, field_name: str, value: Any) -> str:
    """
    Map a choices value to its human label without relying on get_FOO_display
    (which static analyzers may not detect).
    """
    try:
        field = obj._meta.get_field(field_name)  # type: ignore[attr-defined]
        choices = getattr(field, "choices", ()) or ()
        mapping = {str(k): str(v) for k, v in choices}
        return mapping.get(str(value), str(value))
    except Exception:
        return str(value)


def _audit_items(audit: InventoryAudit) -> QuerySet[InventoryAuditItem]:
    """
    Return the items queryset for an audit, regardless of related_name.
    Falls back to filtering by FK if related manager isn't available.
    """
    rel = getattr(audit, "items", None)
    if rel is not None and hasattr(rel, "all"):
        return rel.all()
    return InventoryAuditItem.objects.filter(audit=audit)


# ================================================================
# 🧾 قائمة العناصر مع فلترة + تصدير + PDF
# ================================================================


def inventory_list(request):
    items = InventoryItem.objects.select_related("product")
    query = (request.GET.get("q") or "").strip() or None

    if query:
        Product = apps.get_model("products", "Product")
        # الحقول المحتملة للبحث
        candidates = ["name", "sku", "barcode", "code"]
        existing = {f.name for f in Product._meta.get_fields()}
        lookups = [f"product__{f}__icontains" for f in candidates if f in existing]

        q_obj = Q()
        for lk in lookups:
            q_obj |= Q(**{lk: query})

        # لو مفيش ولا حقل نصّي متاح، خلّيه يبحث بالـ ID كحل أخير
        if not lookups and query.isdigit():
            q_obj |= Q(product__id=int(query))

        items = items.filter(q_obj)

    if request.GET.get("download_pdf") == "1":
        return render_to_pdf(
            "inventory/inventory_pdf.html", {"items": items, "request": request}
        )

    if request.GET.get("export") == "1":
        data = [
            {
                "الاسم": _safe(i.product, "name", ""),
                "الكود": _safe(i.product, "code", ""),
                "الكمية": i.quantity,
                "الوحدة": _choice_label(i, "unit", _safe(i, "unit", "")),
                "الموقع": _safe(i.warehouse, "name", "") if i.warehouse else "",
                "الحد الأدنى": i.min_threshold,
            }
            for i in items
        ]
        return export_to_excel(data, filename="inventory_items.xlsx")

    return render(
        request, "inventory/inventory_list.html", {"items": items, "query": query}
    )


# ================================================================
# ➕ إضافة / تعديل / حذف عنصر مخزون
# ================================================================
def add_inventory_item(request):
    if request.method == "POST":
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ تم إضافة العنصر بنجاح.")
            return redirect("inventory:inventory_list")
    else:
        form = InventoryItemForm()
    return render(
        request,
        "inventory/item_form.html",
        {"form": form, "title": "➕ إضافة عنصر جديد"},
    )


def edit_inventory_item(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == "POST":
        form = InventoryItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ تم تعديل البيانات.")
            return redirect("inventory:inventory_list")
    else:
        form = InventoryItemForm(instance=item)
    return render(
        request, "inventory/item_form.html", {"form": form, "title": "✏️ تعديل عنصر"}
    )


def delete_inventory_item(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == "POST":
        item.delete()
        messages.success(request, "🗑️ تم حذف العنصر.")
        return redirect("inventory:inventory_list")
    return render(request, "inventory/item_delete_confirm.html", {"item": item})


# ================================================================
# 🔄 سجل الحركات + فلترة + PDF + Excel
# ================================================================
def inventory_transactions(request):
    transactions = InventoryMovement.objects.select_related("item").all()
    item_name = request.GET.get("item")
    type_filter = request.GET.get("type")
    date_from = request.GET.get("from")
    date_to = request.GET.get("to")

    if item_name:
        transactions = transactions.filter(item__product__name__icontains=item_name)
    if type_filter:
        transactions = transactions.filter(movement_type=type_filter)
    if date_from:
        transactions = transactions.filter(date__date__gte=date_from)
    if date_to:
        transactions = transactions.filter(date__date__lte=date_to)

    if request.GET.get("download_pdf") == "1":
        return render_to_pdf(
            "inventory/transaction_pdf.html",
            {"transactions": transactions, "request": request},
        )

    if request.GET.get("export") == "1":
        data = [
            {
                "العنصر": _safe(t.item.product, "name", ""),
                "الكمية": t.quantity,
                "النوع": _choice_label(
                    t, "movement_type", _safe(t, "movement_type", "")
                ),
                "الملاحظة": t.note,
                "الوقت": timezone.localtime(t.date).strftime("%Y-%m-%d %H:%M"),
            }
            for t in transactions
        ]
        return export_to_excel(data, filename="inventory_transactions.xlsx")

    return render(
        request,
        "inventory/inventory_transactions.html",
        {
            "transactions": transactions,
            "filters": {
                "item": item_name,
                "type": type_filter,
                "from": date_from,
                "to": date_to,
            },
        },
    )


# ================================================================
# ✅ إضافة حركة مع كشف عجز ذكي
# ================================================================
@login_required
def add_inventory_transaction(request):
    if request.method == "POST":
        form = InventoryTransactionForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            item = movement.item
            new_quantity = item.quantity

            if movement.movement_type == "in":
                new_quantity += movement.quantity
            elif movement.movement_type == "out":
                new_quantity -= movement.quantity
                if new_quantity < 0:
                    RiskIncident.objects.create(
                        user=request.user,
                        event_type="عجز في الجرد",
                        risk_level="HIGH",
                        notes=(
                            f"سحب زائد من {item.product.name}. "
                            f"الكمية الحالية {item.quantity}، المطلوب سحب {movement.quantity}."
                        ),
                    )
                    trigger_risk_alert(
                        "عجز في الجرد",
                        request.user,
                        "مرتفع",
                        f"محاولة سحب كمية غير متوفرة من {item.product.name}",
                    )
                    suspend_user_temporarily(request.user)

                    messages.error(
                        request,
                        "⚠️ لا يمكن تنفيذ العملية. الكمية المطلوبة تتجاوز المخزون المتاح.",
                    )
                    return redirect("inventory:inventory_transactions")

            movement.save()
            item.quantity = new_quantity
            item.save()
            messages.success(request, "✅ تم تنفيذ الحركة بنجاح.")
            return redirect("inventory:inventory_transactions")
    else:
        form = InventoryTransactionForm()

    return render(
        request,
        "inventory/transaction_form.html",
        {"form": form, "title": "➕ حركة مخزنية جديدة"},
    )


# ================================================================
# 📋 الجرد الفعلي الذكي – إنشاء وتحرير
# ================================================================
@login_required
def create_inventory_audit(request):
    if request.method == "POST":
        audit_type = request.POST.get("audit_type")
        audit = InventoryAudit.objects.create(
            audit_type=audit_type, performed_by=request.user
        )
        for item in InventoryItem.objects.select_related("product").all():
            InventoryAuditItem.objects.create(
                audit=audit,
                product=item.product,
                system_quantity=item.quantity,
                physical_quantity=0,
            )
        messages.success(request, "✅ تم إنشاء الجرد، الرجاء إدخال الكميات الفعلية.")
        return redirect("inventory:inventory_audit_edit", audit_id=audit.pk)

    return render(request, "inventory/create_audit.html")


@login_required
def inventory_audit_edit(request, audit_id):
    audit = get_object_or_404(InventoryAudit, id=audit_id)
    if request.method == "POST":
        for item in _audit_items(audit):
            qty = request.POST.get(f"qty_{item.pk}")
            if qty is not None:
                item.physical_quantity = qty
                item.save()
        messages.success(request, "✅ تم حفظ الجرد الفعلي بنجاح.")
        return redirect("inventory:inventory_audit_detail", audit_id=audit.pk)

    return render(request, "inventory/edit_audit.html", {"audit": audit})


# ================================================================
# 📊 تفاصيل الجرد الذكي مع تصدير PDF / Excel
# ================================================================
@login_required
def inventory_audit_detail(request, audit_id):
    audit = get_object_or_404(InventoryAudit, id=audit_id)

    if request.GET.get("pdf") == "1":
        return render_to_pdf(
            "inventory/audit_pdf.html", {"audit": audit, "request": request}
        )

    if request.GET.get("excel") == "1":
        data = [
            {
                "الصنف": item.product.name,
                "النظامي": item.system_quantity,
                "الفعلي": item.physical_quantity,
                "الفرق": item.difference,
                "ملاحظات": item.remarks or "—",
            }
            for item in _audit_items(audit)
        ]
        return export_to_excel(data, filename="audit_report.xlsx")

    return render(request, "inventory/audit_detail.html", {"audit": audit})


# ================================================================
# 🏬 إدارة المخازن (Warehouse Management)
# ================================================================
@login_required
def inventory_locations(request):
    locations = Warehouse.objects.all()
    return render(request, "inventory/warehouse_list.html", {"locations": locations})


@login_required
def add_inventory_location(request):
    if request.method == "POST":
        form = InventoryLocationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ تم إضافة المخزن.")
            return redirect("inventory:inventory_locations")
    else:
        form = InventoryLocationForm()
    return render(
        request,
        "inventory/warehouse_form.html",
        {"form": form, "title": "➕ إضافة مخزن"},
    )


@login_required
def edit_inventory_location(request, pk):
    location = get_object_or_404(Warehouse, pk=pk)
    if request.method == "POST":
        form = InventoryLocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ تم تعديل بيانات المخزن.")
            return redirect("inventory:inventory_locations")
    else:
        form = InventoryLocationForm(instance=location)
    return render(
        request,
        "inventory/warehouse_form.html",
        {"form": form, "title": "✏️ تعديل مخزن"},
    )


@login_required
def delete_inventory_location(request, pk):
    location = get_object_or_404(Warehouse, pk=pk)
    if request.method == "POST":
        location.delete()
        messages.success(request, "🗑️ تم حذف المخزن.")
        return redirect("inventory:inventory_locations")
    return render(
        request, "inventory/warehouse_delete_confirm.html", {"location": location}
    )


def index(request):
    return render(request, "inventory/index.html")


def app_home(request):
    return render(request, "apps/inventory/home.html", {"app": "inventory"})

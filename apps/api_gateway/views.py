from contextlib import suppress
from typing import (Any, Iterable, List, Optional, Protocol, Set, Tuple,
                    TypedDict, cast)

from django.db.models import Model
from django.http import (HttpRequest, HttpResponse, HttpResponseNotAllowed,
                         JsonResponse)
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from apps.accounting.models import CashTransaction
from apps.clients.models import Client
from apps.products.models import Product
from apps.sales.models import SaleInvoice


# ===== Typed schemas & protocols (تصفير الخطوط الحمراء) =====
class HasID(Protocol):
    id: int


class SalesDataItem(TypedDict, total=False):
    id: int
    client: Optional[str]
    total_amount: Any
    date: str


class ProductStockItem(TypedDict, total=False):
    id: int
    name: str
    sku: Optional[str]
    quantity: Any


class CashTxItem(TypedDict, total=False):
    id: int
    amount: Any
    date: str
    description: Optional[str]


# ===== Helpers (مرونة أسماء الحقول والعلاقات) =====
def _field_names(model: type[Model]) -> Set[str]:
    return {f.name for f in model._meta.get_fields()}


def _pick(names: Iterable[str], candidates: Iterable[str]) -> Optional[str]:
    s = set(names)
    for c in candidates:
        if c in s:
            return c
    return None


def _find_fk_to(
    model: type[Model],
    target_model: type[Model],
    fallbacks: Tuple[str, ...] = ("client", "customer", "partner", "contact"),
) -> Optional[str]:
    """ابحث عن اسم حقل FK يشير مباشرة إلى target_model؛ وإلا ارجع أول بديل مطابق."""
    for f in model._meta.get_fields():
        if getattr(f, "is_relation", False) and getattr(f, "many_to_one", False):
            with suppress(Exception):
                if f.remote_field and f.remote_field.model is target_model:
                    return f.name
    return _pick(_field_names(model), fallbacks)


def _name_field_for(
    model: type[Model],
    fallbacks: Tuple[str, ...] = (
        "name",
        "full_name",
        "display_name",
        "company_name",
        "username",
        "title",
    ),
) -> str:
    return _pick(_field_names(model), fallbacks) or "id"


def _coerce_date(v: Any) -> str:
    try:
        return v.isoformat() if hasattr(v, "isoformat") else str(v)
    except Exception:
        return str(v)


def _int_qp(request: HttpRequest, key: str, default: int) -> int:
    try:
        return max(1, int(request.GET.get(key, default)))
    except Exception:
        return default


def _getattr_optional(obj: Any, name: Optional[str], default: Any = None) -> Any:
    """قراءة getattr بأمان عند احتمالية أن يكون اسم الحقل None (لتجنب أخطاء النوع)."""
    if not name:
        return default
    return getattr(obj, name, default)


# ======================= APIs =======================


@csrf_exempt
def sales_data(request: HttpRequest) -> JsonResponse | HttpResponseNotAllowed:
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    # اكتشاف الحقول ديناميكياً
    inv_fields = _field_names(SaleInvoice)
    client_fk = _find_fk_to(SaleInvoice, Client)
    date_f = _pick(inv_fields, ("date_issued", "date", "created_at", "timestamp"))
    total_f = _pick(
        inv_fields, ("total_amount", "total", "amount", "grand_total", "net_total")
    )

    client_name_f = _name_field_for(Client)

    # جلب البيانات
    qs = SaleInvoice.objects.all()
    if client_fk:
        qs = qs.select_related(client_fk)

    limit = _int_qp(request, "limit", 200)
    out: List[SalesDataItem] = []
    for inv in qs.order_by("-id")[:limit]:
        inv_typed = cast(HasID, inv)  # يضمن وجود الخاصية id للـ IDE/mypy

        # اسم العميل
        client_name: Optional[str] = None
        if client_fk:
            cobj = _getattr_optional(inv, client_fk)
            if cobj is not None:
                client_name = _getattr_optional(cobj, client_name_f)

        # القيم الأخرى
        date_val = _getattr_optional(inv, date_f)
        total_val = _getattr_optional(inv, total_f)

        item: SalesDataItem = {
            "id": inv_typed.id,
            "client": client_name,
            "total_amount": total_val,
            "date": _coerce_date(date_val),
        }
        out.append(item)
    return JsonResponse(out, safe=False)


@csrf_exempt
def client_balance(
    request: HttpRequest, client_id: int
) -> JsonResponse | HttpResponseNotAllowed:
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        return JsonResponse({"error": "Client not found"}, status=404)

    name_f = _name_field_for(Client)
    # حاول قراءة balance إن وُجد؛ وإلا 0 (يمكن لاحقًا حسابه من القيود)
    balance = getattr(client, "balance", 0)
    return JsonResponse(
        {"client": getattr(client, name_f, str(client)), "balance": balance}
    )


@csrf_exempt
def product_stock(request: HttpRequest) -> JsonResponse | HttpResponseNotAllowed:
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    prod_fields = _field_names(Product)
    name_f = _pick(prod_fields, ("name", "title", "product_name")) or "id"
    qty_f = _pick(
        prod_fields,
        ("quantity", "qty", "qty_available", "stock", "on_hand", "inventory_qty"),
    )
    sku_f = _pick(prod_fields, ("sku", "code", "barcode"))

    limit = _int_qp(request, "limit", 500)
    out: List[ProductStockItem] = []
    for p in Product.objects.all().order_by("id")[:limit]:
        p_typed = cast(HasID, p)

        item: ProductStockItem = {
            "id": p_typed.id,
            "name": getattr(p, name_f, str(p)),
            "sku": _getattr_optional(p, sku_f),
            "quantity": (_getattr_optional(p, qty_f, 0) if qty_f else 0),
        }
        out.append(item)
    return JsonResponse(out, safe=False)


@csrf_exempt
def cash_transactions(request: HttpRequest) -> JsonResponse | HttpResponseNotAllowed:
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    tx_fields = _field_names(CashTransaction)
    amt_f = _pick(tx_fields, ("amount", "value", "total", "net", "paid"))
    date_f = _pick(tx_fields, ("date", "created_at", "timestamp"))
    desc_f = _pick(tx_fields, ("description", "memo", "note", "details"))

    limit = _int_qp(request, "limit", 300)
    out: List[CashTxItem] = []
    for t in CashTransaction.objects.all().order_by("-id")[:limit]:
        t_typed = cast(HasID, t)

        item: CashTxItem = {
            "id": t_typed.id,
            "amount": _getattr_optional(t, amt_f),
            "date": _coerce_date(_getattr_optional(t, date_f)),
            "description": _getattr_optional(t, desc_f),
        }
        out.append(item)
    return JsonResponse(out, safe=False)


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "api_gateway/index.html")


def app_home(request: HttpRequest) -> HttpResponse:
    return render(request, "apps/api_gateway/home.html", {"app": "api_gateway"})

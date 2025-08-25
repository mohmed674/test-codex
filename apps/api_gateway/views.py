from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Model
from typing import Optional, Iterable

from apps.sales.models import SaleInvoice
from apps.accounting.models import CashTransaction
from apps.products.models import Product
from apps.clients.models import Client


# ===== Helpers (مرونة أسماء الحقول والعلاقات) =====
def _field_names(model: Model) -> set:
    return {f.name for f in model._meta.get_fields()}

def _pick(names: Iterable[str], candidates: Iterable[str]) -> Optional[str]:
    s = set(names)
    for c in candidates:
        if c in s:
            return c
    return None

def _find_fk_to(model, target_model, fallbacks=("client", "customer", "partner", "contact")) -> Optional[str]:
    # ابحث صراحةً عن FK يشير إلى target_model
    for f in model._meta.get_fields():
        if getattr(f, "is_relation", False) and getattr(f, "many_to_one", False):
            try:
                if f.remote_field and f.remote_field.model is target_model:
                    return f.name
            except Exception:
                pass
    # وإلا استخدم أول اسم مطابق من قائمة بديلة
    return _pick(_field_names(model), fallbacks)

def _name_field_for(model, fallbacks=("name", "full_name", "display_name", "company_name", "username", "title")) -> str:
    return _pick(_field_names(model), fallbacks) or "id"

def _coerce_date(v):
    try:
        return v.isoformat() if hasattr(v, "isoformat") else str(v)
    except Exception:
        return str(v)

def _int_qp(request, key: str, default: int) -> int:
    try:
        return max(1, int(request.GET.get(key, default)))
    except Exception:
        return default


# ======================= APIs =======================

@csrf_exempt
def sales_data(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    # اكتشاف الحقول ديناميكياً
    inv_fields = _field_names(SaleInvoice)
    client_fk = _find_fk_to(SaleInvoice, Client)
    date_f = _pick(inv_fields, ("date_issued", "date", "created_at", "timestamp"))
    total_f = _pick(inv_fields, ("total_amount", "total", "amount", "grand_total", "net_total"))

    client_name_f = _name_field_for(Client)

    # جلب البيانات
    qs = SaleInvoice.objects.all()
    if client_fk:
        qs = qs.select_related(client_fk)

    limit = _int_qp(request, "limit", 200)
    out = []
    for inv in qs.order_by('-id')[:limit]:
        # اسم العميل
        client_name = None
        if client_fk:
            cobj = getattr(inv, client_fk, None)
            if cobj is not None:
                client_name = getattr(cobj, client_name_f, None)
        # القيم الأخرى
        date_val = getattr(inv, date_f, None) if date_f else None
        total_val = getattr(inv, total_f, None) if total_f else None

        out.append({
            "id": inv.id,
            "client": client_name,
            "total_amount": total_val,
            "date": _coerce_date(date_val),
        })
    return JsonResponse(out, safe=False)


@csrf_exempt
def client_balance(request, client_id):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        return JsonResponse({'error': 'Client not found'}, status=404)

    name_f = _name_field_for(Client)
    # حاول قراءة balance إن وُجد؛ وإلا 0 (يمكن لاحقًا حسابه من القيود)
    balance = getattr(client, 'balance', 0)
    return JsonResponse({'client': getattr(client, name_f, str(client)), 'balance': balance})


@csrf_exempt
def product_stock(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    prod_fields = _field_names(Product)
    name_f = _pick(prod_fields, ("name", "title", "product_name")) or "id"
    qty_f = _pick(prod_fields, ("quantity", "qty", "qty_available", "stock", "on_hand", "inventory_qty"))
    sku_f = _pick(prod_fields, ("sku", "code", "barcode"))

    limit = _int_qp(request, "limit", 500)
    out = []
    for p in Product.objects.all().order_by('id')[:limit]:
        out.append({
            "id": p.id,
            "name": getattr(p, name_f, str(p)),
            "sku": getattr(p, sku_f, None),
            "quantity": getattr(p, qty_f, 0) if qty_f else 0,
        })
    return JsonResponse(out, safe=False)


@csrf_exempt
def cash_transactions(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    tx_fields = _field_names(CashTransaction)
    amt_f = _pick(tx_fields, ("amount", "value", "total", "net", "paid"))
    date_f = _pick(tx_fields, ("date", "created_at", "timestamp"))
    desc_f = _pick(tx_fields, ("description", "memo", "note", "details"))

    limit = _int_qp(request, "limit", 300)
    out = []
    for t in CashTransaction.objects.all().order_by('-id')[:limit]:
        out.append({
            "id": t.id,
            "amount": getattr(t, amt_f, None) if amt_f else None,
            "date": _coerce_date(getattr(t, date_f, None) if date_f else None),
            "description": getattr(t, desc_f, None) if desc_f else None,
        })
    return JsonResponse(out, safe=False)


from django.shortcuts import render

def index(request):
    return render(request, 'api_gateway/index.html')


def app_home(request):
    return render(request, 'apps/api_gateway/home.html', {'app': 'api_gateway'})

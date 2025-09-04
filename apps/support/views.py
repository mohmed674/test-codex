from contextlib import suppress
from typing import TYPE_CHECKING

from django.apps import apps as dj_apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET, require_http_methods

from .forms import SupportResponseForm, SupportTicketForm

# لا نستورد الموديل الحقيقي لتفادي كسر التشغيل؛ نعرّف Stub للـ type checkers فقط.
if TYPE_CHECKING:  # pragma: no cover
    class _SupportTicket:  # حدّ أدنى لتعريف نوعي بدون استيراد
        ...

def _get_support_ticket_model():
    """
    نجلب نموذج SupportTicket بشكل كسول وآمن أثناء الإقلاع.
    نعيد None إذا لم يكن الموديل موجودًا في تطبيق support.
    """
    try:
        # require_ready=False يمنع LookupError أثناء تحميل urls قبل اكتمال populate()
        return dj_apps.get_model("support", "SupportTicket", require_ready=False)  # type: ignore[call-arg]
    except Exception:
        return None

# صفحة بديلة عند عدم توفر نموذج التذاكر
def _model_missing(request: HttpRequest, where: str) -> HttpResponse:
    messages.error(
        request,
        _(
            "خدمة التذاكر غير مُفعّلة حاليًا أو الموديل غير متاح (الموضع: %(where)s)."
        )
        % {"where": where},
    )
    return render(request, "support/disabled.html", {"where": where}, status=503)

# ======= قوائم/تفاصيل =======
@require_GET
@login_required
def ticket_list(request: HttpRequest) -> HttpResponse:
    SupportTicket = _get_support_ticket_model()
    if SupportTicket is None:
        return _model_missing(request, where="list")
    tickets = SupportTicket.objects.all().order_by("-created_at")  # type: ignore[attr-defined]
    return render(request, "support/ticket_list.html", {"tickets": tickets})

@require_GET
@login_required
def ticket_detail(request: HttpRequest, pk: int) -> HttpResponse:
    SupportTicket = _get_support_ticket_model()
    if SupportTicket is None:
        return _model_missing(request, where="detail")
    ticket = get_object_or_404(SupportTicket, pk=pk)
    responses_mgr = getattr(ticket, "responses", None)
    responses = responses_mgr.all() if responses_mgr is not None else []
    return render(
        request,
        "support/ticket_detail.html",
        {"ticket": ticket, "responses": responses},
    )

# ======= إنشاء/إضافة رد =======
@require_http_methods(["GET", "POST"])
@login_required
@transaction.atomic
def create_ticket(request: HttpRequest) -> HttpResponse:
    SupportTicket = _get_support_ticket_model()
    if SupportTicket is None:
        return _model_missing(request, where="create")
    if request.method == "POST":
        form = SupportTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            # اربط بالعميل إن توفر
            client = getattr(getattr(request.user, "client", None), "pk", None)
            if client is not None:
                with suppress(Exception):
                    ticket.client = request.user.client  # type: ignore[attr-defined]
            ticket.save()
            messages.success(request, _("تم إنشاء التذكرة بنجاح."))
            return redirect("support:ticket_list")
    else:
        form = SupportTicketForm()
    return render(request, "support/support_ticket_form.html", {"form": form})

@require_http_methods(["GET", "POST"])
@login_required
@transaction.atomic
def add_response(request: HttpRequest, pk: int) -> HttpResponse:
    SupportTicket = _get_support_ticket_model()
    if SupportTicket is None:
        return _model_missing(request, where="add_response")
    ticket = get_object_or_404(SupportTicket, pk=pk)
    if request.method == "POST":
        form = SupportResponseForm(request.POST)
        if form.is_valid():
            resp = form.save(commit=False)
            with suppress(Exception):
                resp.ticket = ticket  # type: ignore[attr-defined]
            # اربط الموظف إن أمكن
            employee = getattr(request.user, "employee", None)
            if employee is not None:
                with suppress(Exception):
                    resp.responder = employee  # type: ignore[attr-defined]
            resp.save()
            messages.success(request, _("تمت إضافة الرد بنجاح."))
            return redirect("support:ticket_detail", pk=pk)
    else:
        form = SupportResponseForm()
    return render(
        request, "support/response_form.html", {"form": form, "ticket": ticket}
    )

# ======= صفحات عامة =======
@require_GET
def index(request: HttpRequest) -> HttpResponse:
    return render(request, "support/index.html")

@require_GET
def app_home(request: HttpRequest) -> HttpResponse:
    return render(request, "apps/support/home.html", {"app": "support"})

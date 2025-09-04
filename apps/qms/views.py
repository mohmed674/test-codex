# -*- coding: utf-8 -*-
# QMS Views — AQL / SPC / CAPA
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Optional, Tuple

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, Q, QuerySet
from django.http import (HttpRequest, HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect, JsonResponse)
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import (CreateView, DetailView, ListView,
                                  TemplateView, UpdateView)

from .models import (AQLCodeLetter, AQLPlan, AQLSamplingRow, CAPAAction,
                     CapabilityStudy, CAPARecord, CAPAStatus, ControlChart,
                     ControlProcess, DataPoint, InspectionLot,
                     InspectionResult, Nonconformity, Subgroup)

# =========================
# Helpers
# =========================


def _to_int(v: Any, default: Optional[int] = None) -> Optional[int]:
    try:
        return int(str(v).strip())
    except Exception:
        return default


def _to_decimal(v: Any, default: Optional[Decimal] = None) -> Optional[Decimal]:
    try:
        return Decimal(str(v).strip())
    except (InvalidOperation, Exception):
        return default


def _compute_aql_sampling(
    plan: AQLPlan, lot_size: int
) -> Optional[Tuple[str, int, int, int]]:
    """Returns (code_letter, sample_size, accept, reject) for given plan and lot size."""
    row = (
        AQLCodeLetter.objects.filter(
            plan=plan, lot_size_from__lte=lot_size, lot_size_to__gte=lot_size
        )
        .order_by("lot_size_from", "lot_size_to")
        .first()
    )
    if not row:
        return None
    sr = (
        AQLSamplingRow.objects.filter(plan=plan, code_letter=row.code_letter)
        .order_by("sample_size")
        .first()
    )
    if not sr:
        return None
    return (row.code_letter, sr.sample_size, sr.accept, sr.reject)


# =========================
# QMS Home / Overview
# =========================


class QMSHomeView(LoginRequiredMixin, TemplateView):
    template_name = "apps/qms/index.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx["kpi"] = {
            "plans": AQLPlan.objects.count(),
            "lots": InspectionLot.objects.count(),
            "spc_processes": ControlProcess.objects.filter(is_active=True).count(),
            "capa_open": CAPARecord.objects.filter(
                status__in=[CAPAStatus.OPEN, CAPAStatus.IN_PROGRESS]
            ).count(),
        }
        ctx["recent_lots"] = InspectionLot.objects.select_related(
            "plan", "product", "inventory_item"
        ).order_by("-created_at")[:10]
        ctx["recent_capa"] = CAPARecord.objects.order_by("-created_at")[:10]
        return ctx


# =========================
# AQL — Plans
# =========================


class AQLPlanListView(LoginRequiredMixin, ListView):
    model = AQLPlan
    paginate_by = 25
    template_name = "qms/aql/plan_list.html"
    ordering: tuple[str, ...] = ("-effective_from", "-created_at")

    def get_queryset(self) -> QuerySet[AQLPlan]:
        qs = AQLPlan.objects.all()
        req: HttpRequest = self.request

        # free text
        qval = (req.GET.get("q") or "").strip()
        if qval:
            qs = qs.filter(
                Q(name__icontains=qval)
                | Q(standard__icontains=qval)
                | Q(aql__icontains=qval)
            )

        # date range
        df = (req.GET.get("date_from") or "").strip()
        dt = (req.GET.get("date_to") or "").strip()
        if df:
            try:
                qs = qs.filter(effective_from__date__gte=df)
            except Exception:
                qs = qs.filter(effective_from__gte=df)
        if dt:
            try:
                qs = qs.filter(effective_from__date__lte=dt)
            except Exception:
                qs = qs.filter(effective_from__lte=dt)

        # extras
        if v := (req.GET.get("stage") or "").strip():
            qs = qs.filter(stage=v)
        if v := (req.GET.get("mode") or "").strip():
            qs = qs.filter(mode=v)
        if v := (req.GET.get("level") or "").strip():
            qs = qs.filter(level=v)
        if v := (req.GET.get("active") or "").strip():
            qs = qs.filter(is_active=v in ("1", "true", "True"))
        return qs


class AQLPlanDetailView(LoginRequiredMixin, DetailView):
    model = AQLPlan
    template_name = "qms/aql/plan_detail.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        plan = AQLPlan.objects.get(pk=self.kwargs["pk"])
        ctx["code_letters"] = AQLCodeLetter.objects.filter(plan=plan).order_by(
            "lot_size_from", "lot_size_to"
        )
        ctx["sampling_rows"] = AQLSamplingRow.objects.filter(plan=plan).order_by(
            "code_letter", "sample_size"
        )
        return ctx


class AQLPlanCreateView(LoginRequiredMixin, CreateView):
    model = AQLPlan
    template_name = "qms/aql/plan_form.html"
    fields = [
        "name",
        "standard",
        "stage",
        "level",
        "aql",
        "mode",
        "effective_from",
        "is_active",
    ]
    success_url = reverse_lazy("qms:aql_plan_list")

    def form_valid(self, form: Any) -> HttpResponse:
        messages.success(self.request, _("تم إنشاء خطة AQL بنجاح."))
        return super().form_valid(form)


class AQLPlanUpdateView(LoginRequiredMixin, UpdateView):
    model = AQLPlan
    template_name = "qms/aql/plan_form.html"
    fields = [
        "name",
        "standard",
        "stage",
        "level",
        "aql",
        "mode",
        "effective_from",
        "is_active",
    ]
    success_url = reverse_lazy("qms:aql_plan_list")

    def form_valid(self, form: Any) -> HttpResponse:
        messages.success(self.request, _("تم تحديث خطة AQL بنجاح."))
        return super().form_valid(form)


# =========================
# AQL — Inspection Lots & Results
# =========================


class InspectionLotListView(LoginRequiredMixin, ListView):
    model = InspectionLot
    paginate_by = 25
    template_name = "qms/aql/lot_list.html"
    ordering: tuple[str, ...] = ("-created_at",)
    date_field = "started_at"

    def get_queryset(self) -> QuerySet[InspectionLot]:
        qs = InspectionLot.objects.select_related(
            "plan", "product", "inventory_item", "inspector"
        )
        req: HttpRequest = self.request

        # text
        qval = (req.GET.get("q") or "").strip()
        if qval:
            qs = qs.filter(
                Q(code__icontains=qval)
                | Q(source_ref__icontains=qval)
                | Q(product__name__icontains=qval)
                | Q(inventory_item__product__name__icontains=qval)
            )

        # date range on started_at
        df = (req.GET.get("date_from") or "").strip()
        dt = (req.GET.get("date_to") or "").strip()
        if df:
            try:
                qs = qs.filter(started_at__date__gte=df)
            except Exception:
                qs = qs.filter(started_at__gte=df)
        if dt:
            try:
                qs = qs.filter(started_at__date__lte=dt)
            except Exception:
                qs = qs.filter(started_at__lte=dt)

        # extras
        if v := (req.GET.get("stage") or "").strip():
            qs = qs.filter(stage=v)
        if v := (req.GET.get("decision") or "").strip():
            qs = qs.filter(decision=v)
        if v := (req.GET.get("plan") or "").strip():
            qs = qs.filter(plan_id=v)

        return qs


class InspectionLotDetailView(LoginRequiredMixin, DetailView):
    model = InspectionLot
    template_name = "qms/aql/lot_detail.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        lot = InspectionLot.objects.get(pk=self.kwargs["pk"])
        ctx["results"] = (
            InspectionResult.objects.filter(lot=lot)
            .select_related("characteristic")
            .order_by("created_at")
        )
        ctx["nonconformities"] = (
            Nonconformity.objects.filter(lot=lot)
            .select_related("defect_type")
            .order_by("-count")
        )
        if lot.plan and lot.lot_size and not lot.sample_size:
            ctx["computed_sampling"] = _compute_aql_sampling(lot.plan, lot.lot_size)
        return ctx


class InspectionResultCreateView(LoginRequiredMixin, CreateView):
    model = InspectionResult
    template_name = "qms/aql/result_form.html"
    fields = [
        "lot",
        "characteristic",
        "value",
        "defects_critical",
        "defects_major",
        "defects_minor",
        "is_pass",
    ]

    def form_valid(self, form: Any) -> HttpResponse:
        obj: InspectionResult = form.save()
        messages.success(self.request, _("تم تسجيل نتيجة الفحص."))
        return HttpResponseRedirect(
            reverse("qms:aql_lot_detail", kwargs={"pk": obj.lot.pk})
        )


class InspectionLotCreateView(LoginRequiredMixin, CreateView):
    model = InspectionLot
    template_name = "qms/aql/lot_form.html"
    fields = [
        "stage",
        "plan",
        "product",
        "inventory_item",
        "source_ct",
        "source_id",
        "source_ref",
        "lot_size",
        "code_letter",
        "sample_size",
        "accept_number",
        "reject_number",
        "started_at",
        "inspector",
        "decision",
        "decision_reason",
        "completed_at",
    ]
    success_url = reverse_lazy("qms:aql_lot_list")

    def form_valid(self, form: Any) -> HttpResponse:
        obj: InspectionLot = form.instance
        if obj.plan and obj.lot_size and not obj.sample_size:
            comp = _compute_aql_sampling(obj.plan, obj.lot_size)
            if comp:
                (
                    obj.code_letter,
                    obj.sample_size,
                    obj.accept_number,
                    obj.reject_number,
                ) = comp
        messages.success(self.request, _("تم إنشاء دفعة فحص AQL."))
        return super().form_valid(form)


class InspectionLotUpdateView(LoginRequiredMixin, UpdateView):
    model = InspectionLot
    template_name = "qms/aql/lot_form.html"
    fields = [
        "stage",
        "plan",
        "product",
        "inventory_item",
        "source_ct",
        "source_id",
        "source_ref",
        "lot_size",
        "code_letter",
        "sample_size",
        "accept_number",
        "reject_number",
        "started_at",
        "inspector",
        "decision",
        "decision_reason",
        "completed_at",
    ]
    success_url = reverse_lazy("qms:aql_lot_list")

    def form_valid(self, form: Any) -> HttpResponse:
        messages.success(self.request, _("تم تحديث دفعة الفحص."))
        return super().form_valid(form)


class AQLComputeSamplingView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        plan_id = _to_int(request.GET.get("plan"))
        lot_size = _to_int(request.GET.get("lot_size"))
        if not plan_id or not lot_size:
            return HttpResponseBadRequest("plan & lot_size are required")
        try:
            plan = AQLPlan.objects.get(pk=plan_id)
        except AQLPlan.DoesNotExist:
            return HttpResponseBadRequest("Invalid plan")
        comp = _compute_aql_sampling(plan, lot_size)
        if not comp:
            return JsonResponse({"found": False})
        code_letter, sample_size, ac, re = comp
        return JsonResponse(
            {
                "found": True,
                "code_letter": code_letter,
                "sample_size": sample_size,
                "accept": ac,
                "reject": re,
            }
        )


# =========================
# SPC — Processes & Charts
# =========================


class ControlProcessListView(LoginRequiredMixin, ListView):
    model = ControlProcess
    paginate_by = 25
    template_name = "qms/spc/process_list.html"
    ordering: tuple[str, ...] = ("key",)

    def get_queryset(self) -> QuerySet[ControlProcess]:
        qs = ControlProcess.objects.all()
        req: HttpRequest = self.request

        qval = (req.GET.get("q") or "").strip()
        if qval:
            qs = qs.filter(
                Q(key__icontains=qval)
                | Q(name__icontains=qval)
                | Q(product__name__icontains=qval)
            )

        if v := (req.GET.get("active") or "").strip():
            qs = qs.filter(is_active=v in ("1", "true", "True"))

        return qs


class ControlProcessDetailView(LoginRequiredMixin, DetailView):
    model = ControlProcess
    template_name = "qms/spc/process_detail.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        proc = ControlProcess.objects.get(pk=self.kwargs["pk"])
        ctx["charts"] = ControlChart.objects.filter(process=proc).order_by(
            "-created_at"
        )
        ctx["capabilities"] = CapabilityStudy.objects.filter(process=proc).order_by(
            "-created_at"
        )[:8]
        return ctx


class ControlProcessCreateView(LoginRequiredMixin, CreateView):
    model = ControlProcess
    template_name = "qms/spc/process_form.html"
    fields = ["key", "name", "product", "inventory_item", "characteristic", "is_active"]
    success_url = reverse_lazy("qms:spc_process_list")

    def form_valid(self, form: Any) -> HttpResponse:
        obj: ControlProcess = form.save()
        messages.success(self.request, _("تم إنشاء عملية SPC."))
        return HttpResponseRedirect(
            reverse("qms:spc_process_detail", kwargs={"pk": obj.pk})
        )


class ControlProcessUpdateView(LoginRequiredMixin, UpdateView):
    model = ControlProcess
    template_name = "qms/spc/process_form.html"
    fields = ["key", "name", "product", "inventory_item", "characteristic", "is_active"]
    success_url = reverse_lazy("qms:spc_process_list")

    def form_valid(self, form: Any) -> HttpResponse:
        obj: ControlProcess = form.save()
        messages.success(self.request, _("تم تحديث عملية SPC."))
        return HttpResponseRedirect(
            reverse("qms:spc_process_detail", kwargs={"pk": obj.pk})
        )


class ControlChartListView(LoginRequiredMixin, ListView):
    model = ControlChart
    paginate_by = 25
    template_name = "qms/spc/chart_list.html"
    ordering: tuple[str, ...] = ("-created_at",)

    def get_queryset(self) -> QuerySet[ControlChart]:
        qs = ControlChart.objects.all()
        req: HttpRequest = self.request

        qval = (req.GET.get("q") or "").strip()
        if qval:
            qs = qs.filter(
                Q(process__name__icontains=qval) | Q(process__key__icontains=qval)
            )

        if v := (req.GET.get("type") or "").strip():
            qs = qs.filter(chart_type=v)
        if v := (req.GET.get("rule") or "").strip():
            qs = qs.filter(rule_set=v)
        if v := (req.GET.get("active") or "").strip():
            qs = qs.filter(is_active=v in ("1", "true", "True"))

        return qs


class ControlChartDetailView(LoginRequiredMixin, DetailView):
    model = ControlChart
    template_name = "qms/spc/chart_detail.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        chart = ControlChart.objects.get(pk=self.kwargs["pk"])
        subgroups = Subgroup.objects.filter(chart=chart).order_by("number")
        ctx["subgroups"] = subgroups
        ctx["stats"] = subgroups.aggregate(
            n=Count("id"), mean_avg=Avg("mean"), r_avg=Avg("r"), s_avg=Avg("s")
        )
        return ctx


class ControlChartCreateView(LoginRequiredMixin, CreateView):
    model = ControlChart
    template_name = "qms/spc/chart_form.html"
    fields = [
        "process",
        "chart_type",
        "subgroup_size",
        "rule_set",
        "cl",
        "ucl",
        "lcl",
        "auto_calculated",
        "effective_from",
        "is_active",
    ]

    def form_valid(self, form: Any) -> HttpResponse:
        obj: ControlChart = form.save()
        messages.success(self.request, _("تم إنشاء مخطط SPC."))
        return HttpResponseRedirect(
            reverse("qms:spc_chart_detail", kwargs={"pk": obj.pk})
        )


class ControlChartUpdateView(LoginRequiredMixin, UpdateView):
    model = ControlChart
    template_name = "qms/spc/chart_form.html"
    fields = [
        "process",
        "chart_type",
        "subgroup_size",
        "rule_set",
        "cl",
        "ucl",
        "lcl",
        "auto_calculated",
        "effective_from",
        "is_active",
    ]

    def form_valid(self, form: Any) -> HttpResponse:
        obj: ControlChart = form.save()
        messages.success(self.request, _("تم تحديث مخطط SPC."))
        return HttpResponseRedirect(
            reverse("qms:spc_chart_detail", kwargs={"pk": obj.pk})
        )


class SubgroupListView(LoginRequiredMixin, ListView):
    model = Subgroup
    paginate_by = 50
    template_name = "qms/spc/subgroup_list.html"

    def get_queryset(self) -> QuerySet[Subgroup]:
        chart_id = _to_int(self.kwargs.get("chart_id"))
        return Subgroup.objects.filter(chart_id=chart_id).order_by("number")


class SubgroupCreateView(LoginRequiredMixin, CreateView):
    model = Subgroup
    template_name = "qms/spc/subgroup_form.html"
    fields = ["chart", "number", "timestamp", "n", "mean", "r", "s"]

    def get_initial(self) -> Dict[str, Any]:
        initial = super().get_initial()
        chart_id = _to_int(self.kwargs.get("chart_id"))
        if chart_id:
            initial["chart"] = chart_id
            last = (
                Subgroup.objects.filter(chart_id=chart_id)
                .order_by("-number")
                .values_list("number", flat=True)
                .first()
            )
            if last:
                initial["number"] = last + 1
        return initial

    def form_valid(self, form: Any) -> HttpResponse:
        obj: Subgroup = form.save()
        messages.success(self.request, _("تم إنشاء المجموعة الفرعية."))
        return HttpResponseRedirect(
            reverse("qms:spc_chart_detail", kwargs={"pk": obj.chart.pk})
        )


class DataPointCreateView(LoginRequiredMixin, CreateView):
    model = DataPoint
    template_name = "qms/spc/point_form.html"
    fields = ["subgroup", "value", "defects", "sample_size", "is_out_of_control"]

    def get_initial(self) -> Dict[str, Any]:
        initial = super().get_initial()
        sg_id = _to_int(self.kwargs.get("subgroup_id"))
        if sg_id:
            initial["subgroup"] = sg_id
        return initial

    def form_valid(self, form: Any) -> HttpResponse:
        obj: DataPoint = form.save()
        messages.success(self.request, _("تم إضافة نقطة البيانات."))
        return HttpResponseRedirect(
            reverse("qms:spc_chart_detail", kwargs={"pk": obj.subgroup.chart.pk})
        )


# =========================
# CAPA — Records & Actions
# =========================


class CAPARecordListView(LoginRequiredMixin, ListView):
    model = CAPARecord
    paginate_by = 25
    template_name = "qms/capa/record_list.html"
    ordering: tuple[str, ...] = ("-created_at",)

    def get_queryset(self) -> QuerySet[CAPARecord]:
        qs = CAPARecord.objects.all()
        req: HttpRequest = self.request

        qval = (req.GET.get("q") or "").strip()
        if qval:
            qs = qs.filter(
                Q(code__icontains=qval)
                | Q(title__icontains=qval)
                | Q(source_ref__icontains=qval)
            )

        if v := (req.GET.get("status") or "").strip():
            qs = qs.filter(status=v)
        if v := (req.GET.get("type") or "").strip():
            qs = qs.filter(capa_type=v)

        return qs


class CAPARecordDetailView(LoginRequiredMixin, DetailView):
    model = CAPARecord
    template_name = "qms/capa/record_detail.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        rec = CAPARecord.objects.get(pk=self.kwargs["pk"])
        ctx["actions"] = CAPAAction.objects.filter(record=rec).order_by("-created_at")
        return ctx


class CAPARecordCreateView(LoginRequiredMixin, CreateView):
    model = CAPARecord
    template_name = "qms/capa/record_form.html"
    fields = [
        "title",
        "capa_type",
        "status",
        "source_ct",
        "source_id",
        "source_ref",
        "severity",
        "occurrence",
        "detection",
        "owner",
        "due_date",
        "root_cause_method",
        "root_cause",
        "containment",
        "attachments",
    ]

    def form_valid(self, form: Any) -> HttpResponse:
        obj: CAPARecord = form.save()
        messages.success(self.request, _("تم إنشاء سجل CAPA."))
        return HttpResponseRedirect(
            reverse("qms:capa_record_detail", kwargs={"pk": obj.pk})
        )


class CAPARecordUpdateView(LoginRequiredMixin, UpdateView):
    model = CAPARecord
    template_name = "qms/capa/record_form.html"
    fields = [
        "title",
        "capa_type",
        "status",
        "source_ct",
        "source_id",
        "source_ref",
        "severity",
        "occurrence",
        "detection",
        "owner",
        "due_date",
        "root_cause_method",
        "root_cause",
        "containment",
        "attachments",
        "effectiveness_verified_at",
        "effectiveness_verified_by",
    ]

    def form_valid(self, form: Any) -> HttpResponse:
        obj: CAPARecord = form.save()
        messages.success(self.request, _("تم تحديث سجل CAPA."))
        return HttpResponseRedirect(
            reverse("qms:capa_record_detail", kwargs={"pk": obj.pk})
        )


class CAPAActionCreateView(LoginRequiredMixin, CreateView):
    model = CAPAAction
    template_name = "qms/capa/action_form.html"
    fields = [
        "record",
        "action_type",
        "description",
        "owner",
        "due_date",
        "status",
        "implemented_at",
        "verified_at",
        "verification_result",
    ]

    def get_initial(self) -> Dict[str, Any]:
        initial = super().get_initial()
        rec_id = _to_int(self.kwargs.get("record_id"))
        if rec_id:
            initial["record"] = rec_id
        return initial

    def form_valid(self, form: Any) -> HttpResponse:
        obj: CAPAAction = form.save()
        messages.success(self.request, _("تم إضافة إجراء CAPA."))
        return HttpResponseRedirect(
            reverse("qms:capa_record_detail", kwargs={"pk": obj.record.pk})
        )


class CAPAActionUpdateView(LoginRequiredMixin, UpdateView):
    model = CAPAAction
    template_name = "qms/capa/action_form.html"
    fields = [
        "record",
        "action_type",
        "description",
        "owner",
        "due_date",
        "status",
        "implemented_at",
        "verified_at",
        "verification_result",
    ]

    def form_valid(self, form: Any) -> HttpResponse:
        obj: CAPAAction = form.save()
        messages.success(self.request, _("تم تحديث إجراء CAPA."))
        return HttpResponseRedirect(
            reverse("qms:capa_record_detail", kwargs={"pk": obj.record.pk})
        )


class CAPAChangeStatusView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        rec_id = _to_int(request.POST.get("id"))
        status = (request.POST.get("status") or "").strip()
        if not rec_id or status not in CAPAStatus.values:
            return JsonResponse({"ok": False, "error": "invalid"}, status=400)
        try:
            rec = CAPARecord.objects.get(pk=rec_id)
        except CAPARecord.DoesNotExist:
            return JsonResponse({"ok": False, "error": "not found"}, status=404)
        rec.status = status
        if status == CAPAStatus.VERIFIED and not rec.effectiveness_verified_at:
            rec.effectiveness_verified_at = timezone.now()
            if (
                hasattr(request.user, "is_authenticated")
                and request.user.is_authenticated
            ):
                rec.effectiveness_verified_by = request.user
            else:
                rec.effectiveness_verified_by = None
        rec.save(
            update_fields=[
                "status",
                "effectiveness_verified_at",
                "effectiveness_verified_by",
            ]
        )
        return JsonResponse({"ok": True, "status": rec.status})


# =========================
# Function-based helpers
# =========================


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "qms/index.html")


def app_home(request: HttpRequest) -> HttpResponse:
    return render(request, "apps/qms/home.html", {"app": "qms"})

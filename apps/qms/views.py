# -*- coding: utf-8 -*-
# QMS Views — AQL / SPC / CAPA
# Class-Based Views aligned with Odoo/SAP UX best-practices (through 2025)
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Optional, Tuple

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count, Avg
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, UpdateView
)

from .models import (
    # Masters
    QualityCharacteristic, DefectType,
    # AQL
    AQLPlan, AQLCodeLetter, AQLSamplingRow, InspectionStage, InspectionLot, InspectionResult,
    # SPC
    ControlProcess, ControlChart, Subgroup, DataPoint, ChartType, RuleSet, CapabilityStudy,
    # CAPA
    CAPARecord, CAPAAction, CAPAType, CAPAStatus
)

# =========================
# Helpers / Mixins
# =========================

class QueryFilterMixin:
    """Generic GET-based filtering for list views."""
    search_param = "q"
    date_from_param = "date_from"
    date_to_param = "date_to"
    date_field = "created_at"
    extra_filters_map = None  # dict[str, str] -> map(GET key -> model field)

    def get_queryset(self):
        qs = super().get_queryset()
        q = (self.request.GET.get(self.search_param) or "").strip()
        if q:
            qs = self.apply_search(qs, q)

        df = (self.request.GET.get(self.date_from_param) or "").strip()
        dt = (self.request.GET.get(self.date_to_param) or "").strip()
        if df:
            try:
                qs = qs.filter(**{f"{self.date_field}__date__gte": df})
            except Exception:
                qs = qs.filter(**{f"{self.date_field}__gte": df})
        if dt:
            try:
                qs = qs.filter(**{f"{self.date_field}__date__lte": dt})
            except Exception:
                qs = qs.filter(**{f"{self.date_field}__lte": dt})

        if isinstance(self.extra_filters_map, dict):
            for gkey, fkey in self.extra_filters_map.items():
                val = (self.request.GET.get(gkey) or "").strip()
                if val:
                    try:
                        qs = qs.filter(**{fkey: val})
                    except Exception:
                        pass
        return qs

    def apply_search(self, qs, q: str):
        return qs


def _to_int(v, default: Optional[int] = None) -> Optional[int]:
    try:
        return int(str(v).strip())
    except Exception:
        return default


def _to_decimal(v, default: Optional[Decimal] = None) -> Optional[Decimal]:
    try:
        return Decimal(str(v).strip())
    except (InvalidOperation, Exception):
        return default


def _compute_aql_sampling(plan: AQLPlan, lot_size: int) -> Optional[Tuple[str, int, int, int]]:
    """
    Returns (code_letter, sample_size, accept, reject) for given plan and lot size.
    """
    row = (
        AQLCodeLetter.objects.filter(plan=plan, lot_size_from__lte=lot_size, lot_size_to__gte=lot_size)
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
    template_name = "apps/qms/index.html"  # <-- مطابق لمسارك الفعلي

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["kpi"] = {
            "plans": AQLPlan.objects.count(),
            "lots": InspectionLot.objects.count(),
            "spc_processes": ControlProcess.objects.filter(is_active=True).count(),
            "capa_open": CAPARecord.objects.filter(status__in=[CAPAStatus.OPEN, CAPAStatus.IN_PROGRESS]).count(),
        }
        ctx["recent_lots"] = (
            InspectionLot.objects.select_related("plan", "product", "inventory_item")
            .order_by("-created_at")[:10]
        )
        ctx["recent_capa"] = CAPARecord.objects.order_by("-created_at")[:10]
        return ctx


# =========================
# AQL — Plans
# =========================

class AQLPlanListView(LoginRequiredMixin, QueryFilterMixin, ListView):
    model = AQLPlan
    paginate_by = 25
    template_name = "qms/aql/plan_list.html"
    ordering = ("-effective_from", "-created_at")
    extra_filters_map = {"stage": "stage", "mode": "mode", "level": "level", "active": "is_active"}

    def apply_search(self, qs, q: str):
        return qs.filter(Q(name__icontains=q) | Q(standard__icontains=q) | Q(aql__icontains=q))


class AQLPlanDetailView(LoginRequiredMixin, DetailView):
    model = AQLPlan
    template_name = "qms/aql/plan_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        plan = self.object
        ctx["code_letters"] = plan.code_letters.order_by("lot_size_from", "lot_size_to")
        ctx["sampling_rows"] = plan.sampling_rows.order_by("code_letter", "sample_size")
        return ctx


class AQLPlanCreateView(LoginRequiredMixin, CreateView):
    model = AQLPlan
    template_name = "qms/aql/plan_form.html"
    fields = ["name", "standard", "stage", "level", "aql", "mode", "effective_from", "is_active"]
    success_url = reverse_lazy("qms:aql_plan_list")

    def form_valid(self, form):
        messages.success(self.request, _("تم إنشاء خطة AQL بنجاح."))
        return super().form_valid(form)


class AQLPlanUpdateView(LoginRequiredMixin, UpdateView):
    model = AQLPlan
    template_name = "qms/aql/plan_form.html"
    fields = ["name", "standard", "stage", "level", "aql", "mode", "effective_from", "is_active"]
    success_url = reverse_lazy("qms:aql_plan_list")

    def form_valid(self, form):
        messages.success(self.request, _("تم تحديث خطة AQL بنجاح."))
        return super().form_valid(form)


# =========================
# AQL — Inspection Lots & Results
# =========================

class InspectionLotListView(LoginRequiredMixin, QueryFilterMixin, ListView):
    model = InspectionLot
    paginate_by = 25
    template_name = "qms/aql/lot_list.html"
    ordering = ("-created_at",)
    extra_filters_map = {"stage": "stage", "decision": "decision", "plan": "plan_id"}
    date_field = "started_at"

    def get_queryset(self):
        qs = super().get_queryset().select_related("plan", "product", "inventory_item", "inspector")
        return qs

    def apply_search(self, qs, q: str):
        return qs.filter(
            Q(code__icontains=q) |
            Q(source_ref__icontains=q) |
            Q(product__name__icontains=q) |
            Q(inventory_item__product__name__icontains=q)
        )


class InspectionLotDetailView(LoginRequiredMixin, DetailView):
    model = InspectionLot
    template_name = "qms/aql/lot_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        lot = self.object
        ctx["results"] = lot.results.select_related("characteristic").all().order_by("created_at")
        ctx["nonconformities"] = lot.nonconformities.select_related("defect_type")
        if lot.plan and lot.lot_size and not lot.sample_size:
            comp = _compute_aql_sampling(lot.plan, lot.lot_size)
            ctx["computed_sampling"] = comp
        return ctx


class InspectionLotCreateView(LoginRequiredMixin, CreateView):
    model = InspectionLot
    template_name = "qms/aql/lot_form.html"
    fields = [
        "stage", "plan", "product", "inventory_item",
        "source_ct", "source_id", "source_ref",
        "lot_size",
        "code_letter", "sample_size", "accept_number", "reject_number",
        "started_at", "inspector", "decision", "decision_reason", "completed_at",
    ]
    success_url = reverse_lazy("qms:aql_lot_list")

    def form_valid(self, form):
        obj: InspectionLot = form.instance
        if obj.plan and obj.lot_size and not obj.sample_size:
            comp = _compute_aql_sampling(obj.plan, obj.lot_size)
            if comp:
                obj.code_letter, obj.sample_size, obj.accept_number, obj.reject_number = comp
        messages.success(self.request, _("تم إنشاء دفعة فحص AQL."))
        return super().form_valid(form)


class InspectionLotUpdateView(LoginRequiredMixin, UpdateView):
    model = InspectionLot
    template_name = "qms/aql/lot_form.html"
    fields = [
        "stage", "plan", "product", "inventory_item",
        "source_ct", "source_id", "source_ref",
        "lot_size", "code_letter", "sample_size", "accept_number", "reject_number",
        "started_at", "inspector", "decision", "decision_reason", "completed_at",
    ]
    success_url = reverse_lazy("qms:aql_lot_list")

    def form_valid(self, form):
        messages.success(self.request, _("تم تحديث دفعة الفحص."))
        return super().form_valid(form)


class InspectionResultCreateView(LoginRequiredMixin, CreateView):
    model = InspectionResult
    template_name = "qms/aql/result_form.html"
    fields = [
        "lot", "characteristic", "value",
        "defects_critical", "defects_major", "defects_minor", "is_pass",
    ]

    def get_success_url(self):
        return reverse("qms:aql_lot_detail", kwargs={"pk": self.object.lot_id})

    def form_valid(self, form):
        messages.success(self.request, _("تم تسجيل نتيجة الفحص."))
        return super().form_valid(form)


class AQLComputeSamplingView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
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
        return JsonResponse({
            "found": True,
            "code_letter": code_letter,
            "sample_size": sample_size,
            "accept": ac,
            "reject": re,
        })


# =========================
# SPC — Processes & Charts
# =========================

class ControlProcessListView(LoginRequiredMixin, QueryFilterMixin, ListView):
    model = ControlProcess
    paginate_by = 25
    template_name = "qms/spc/process_list.html"
    ordering = ("key",)
    extra_filters_map = {"active": "is_active"}

    def apply_search(self, qs, q: str):
        return qs.filter(Q(key__icontains=q) | Q(name__icontains=q) | Q(product__name__icontains=q))


class ControlProcessDetailView(LoginRequiredMixin, DetailView):
    model = ControlProcess
    template_name = "qms/spc/process_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        proc = self.object
        ctx["charts"] = proc.charts.order_by("-created_at")
        ctx["capabilities"] = proc.capability_studies.order_by("-created_at")[:8]
        return ctx


class ControlProcessCreateView(LoginRequiredMixin, CreateView):
    model = ControlProcess
    template_name = "qms/spc/process_form.html"
    fields = ["key", "name", "product", "inventory_item", "characteristic", "is_active"]
    success_url = reverse_lazy("qms:spc_process_list")

    def form_valid(self, form):
        messages.success(self.request, _("تم إنشاء عملية SPC."))
        return super().form_valid(form)


class ControlProcessUpdateView(LoginRequiredMixin, UpdateView):
    model = ControlProcess
    template_name = "qms/spc/process_form.html"
    fields = ["key", "name", "product", "inventory_item", "characteristic", "is_active"]
    success_url = reverse_lazy("qms:spc_process_list")

    def form_valid(self, form):
        messages.success(self.request, _("تم تحديث عملية SPC."))
        return super().form_valid(form)


class ControlChartListView(LoginRequiredMixin, QueryFilterMixin, ListView):
    model = ControlChart
    paginate_by = 25
    template_name = "qms/spc/chart_list.html"
    ordering = ("-created_at",)
    extra_filters_map = {"type": "chart_type", "rule": "rule_set", "active": "is_active"}

    def apply_search(self, qs, q: str):
        return qs.filter(Q(process__name__icontains=q) | Q(process__key__icontains=q))


class ControlChartDetailView(LoginRequiredMixin, DetailView):
    model = ControlChart
    template_name = "qms/spc/chart_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        chart = self.object
        ctx["subgroups"] = chart.subgroups.order_by("number")
        stats = chart.subgroups.aggregate(
            n=Count("id"),
            mean_avg=Avg("mean"),
            r_avg=Avg("r"),
            s_avg=Avg("s")
        )
        ctx["stats"] = stats
        return ctx


class ControlChartCreateView(LoginRequiredMixin, CreateView):
    model = ControlChart
    template_name = "qms/spc/chart_form.html"
    fields = ["process", "chart_type", "subgroup_size", "rule_set", "cl", "ucl", "lcl", "auto_calculated", "effective_from", "is_active"]
    success_url = reverse_lazy("qms:spc_chart_list")

    def form_valid(self, form):
        messages.success(self.request, _("تم إنشاء مخطط SPC."))
        return super().form_valid(form)


class ControlChartUpdateView(LoginRequiredMixin, UpdateView):
    model = ControlChart
    template_name = "qms/spc/chart_form.html"
    fields = ["process", "chart_type", "subgroup_size", "rule_set", "cl", "ucl", "lcl", "auto_calculated", "effective_from", "is_active"]
    success_url = reverse_lazy("qms:spc_chart_list")

    def form_valid(self, form):
        messages.success(self.request, _("تم تحديث مخطط SPC."))
        return super().form_valid(form)


class SubgroupListView(LoginRequiredMixin, ListView):
    model = Subgroup
    paginate_by = 50
    template_name = "qms/spc/subgroup_list.html"

    def get_queryset(self):
        chart_id = _to_int(self.kwargs.get("chart_id"))
        return Subgroup.objects.filter(chart_id=chart_id).order_by("number")


class SubgroupCreateView(LoginRequiredMixin, CreateView):
    model = Subgroup
    template_name = "qms/spc/subgroup_form.html"
    fields = ["chart", "number", "timestamp", "n", "mean", "r", "s"]

    def get_initial(self):
        initial = super().get_initial()
        chart_id = _to_int(self.kwargs.get("chart_id"))
        if chart_id:
            initial["chart"] = chart_id
            last = Subgroup.objects.filter(chart_id=chart_id).order_by("-number").values_list("number", flat=True).first()
            if last:
                initial["number"] = last + 1
        return initial

    def get_success_url(self):
        return reverse("qms:spc_chart_detail", kwargs={"pk": self.object.chart_id})

    def form_valid(self, form):
        messages.success(self.request, _("تم إنشاء المجموعة الفرعية."))
        return super().form_valid(form)


class DataPointCreateView(LoginRequiredMixin, CreateView):
    model = DataPoint
    template_name = "qms/spc/point_form.html"
    fields = ["subgroup", "value", "defects", "sample_size", "is_out_of_control"]

    def get_initial(self):
        initial = super().get_initial()
        sg_id = _to_int(self.kwargs.get("subgroup_id"))
        if sg_id:
            initial["subgroup"] = sg_id
        return initial

    def get_success_url(self):
        sg = self.object.subgroup
        return reverse("qms:spc_chart_detail", kwargs={"pk": sg.chart_id})

    def form_valid(self, form):
        messages.success(self.request, _("تم إضافة نقطة البيانات."))
        return super().form_valid(form)


# =========================
# CAPA — Records & Actions
# =========================

class CAPARecordListView(LoginRequiredMixin, QueryFilterMixin, ListView):
    model = CAPARecord
    paginate_by = 25
    template_name = "qms/capa/record_list.html"
    ordering = ("-created_at",)
    extra_filters_map = {"status": "status", "type": "capa_type"}

    def apply_search(self, qs, q: str):
        return qs.filter(Q(code__icontains=q) | Q(title__icontains=q) | Q(source_ref__icontains=q))


class CAPARecordDetailView(LoginRequiredMixin, DetailView):
    model = CAPARecord
    template_name = "qms/capa/record_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        rec = self.object
        ctx["actions"] = rec.actions.order_by("-created_at")
        return ctx


class CAPARecordCreateView(LoginRequiredMixin, CreateView):
    model = CAPARecord
    template_name = "qms/capa/record_form.html"
    fields = [
        "title", "capa_type", "status",
        "source_ct", "source_id", "source_ref",
        "severity", "occurrence", "detection",
        "owner", "due_date",
        "root_cause_method", "root_cause", "containment",
        "attachments",
    ]
    success_url = reverse_lazy("qms:capa_record_list")

    def form_valid(self, form):
        messages.success(self.request, _("تم إنشاء سجل CAPA."))
        return super().form_valid(form)


class CAPARecordUpdateView(LoginRequiredMixin, UpdateView):
    model = CAPARecord
    template_name = "qms/capa/record_form.html"
    fields = [
        "title", "capa_type", "status",
        "source_ct", "source_id", "source_ref",
        "severity", "occurrence", "detection",
        "owner", "due_date",
        "root_cause_method", "root_cause", "containment",
        "attachments", "effectiveness_verified_at", "effectiveness_verified_by",
    ]
    success_url = reverse_lazy("qms:capa_record_list")

    def form_valid(self, form):
        messages.success(self.request, _("تم تحديث سجل CAPA."))
        return super().form_valid(form)


class CAPAActionCreateView(LoginRequiredMixin, CreateView):
    model = CAPAAction
    template_name = "qms/capa/action_form.html"
    fields = ["record", "action_type", "description", "owner", "due_date", "status", "implemented_at", "verified_at", "verification_result"]

    def get_initial(self):
        initial = super().get_initial()
        rec_id = _to_int(self.kwargs.get("record_id"))
        if rec_id:
            initial["record"] = rec_id
        return initial

    def get_success_url(self):
        return reverse("qms:capa_record_detail", kwargs={"pk": self.object.record_id})

    def form_valid(self, form):
        messages.success(self.request, _("تم إضافة إجراء CAPA."))
        return super().form_valid(form)


class CAPAActionUpdateView(LoginRequiredMixin, UpdateView):
    model = CAPAAction
    template_name = "qms/capa/action_form.html"
    fields = ["record", "action_type", "description", "owner", "due_date", "status", "implemented_at", "verified_at", "verification_result"]

    def get_success_url(self):
        return reverse("qms:capa_record_detail", kwargs={"pk": self.object.record_id})

    def form_valid(self, form):
        messages.success(self.request, _("تم تحديث إجراء CAPA."))
        return super().form_valid(form)


class CAPAChangeStatusView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        rec_id = _to_int(request.POST.get("id"))
        status = (request.POST.get("status") or "").strip()
        if not rec_id or status not in CAPAStatus.values:
            return HttpResponseBadRequest("invalid")
        try:
            rec = CAPARecord.objects.get(pk=rec_id)
        except CAPARecord.DoesNotExist:
            return HttpResponseBadRequest("not found")
        rec.status = status
        if status == CAPAStatus.VERIFIED and not rec.effectiveness_verified_at:
            rec.effectiveness_verified_at = timezone.now()
            rec.effectiveness_verified_by = request.user
        rec.save(update_fields=["status", "effectiveness_verified_at", "effectiveness_verified_by"])
        return JsonResponse({"ok": True, "status": rec.status})


from django.shortcuts import render

def index(request):
    return render(request, 'qms/index.html')


def app_home(request):
    return render(request, 'apps/qms/home.html', {'app': 'qms'})

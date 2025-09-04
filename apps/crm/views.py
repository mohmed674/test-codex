# apps/crm/views.py
from __future__ import annotations

from typing import Iterable

from django.apps import apps
from django.shortcuts import get_object_or_404, redirect, render

from .forms import InteractionForm, OpportunityForm
from .models import Lead, Opportunity


def _lead_interactions(lead: Lead) -> Iterable:
    """
    Return interactions for a lead regardless of related_name:
    tries `lead.interactions.all()`, then `lead.interaction_set.all()`,
    finally queries a concrete Interaction model if present.
    """
    for rel_name in ("interactions", "interaction_set"):
        rel = getattr(lead, rel_name, None)
        if rel is not None and hasattr(rel, "all"):
            try:
                return rel.all().order_by("-id")
            except Exception:
                return rel.all()

    Interaction = apps.get_model("crm", "Interaction")
    if Interaction is not None:
        try:
            # Discover FK field pointing to Lead dynamically
            for f in Interaction._meta.get_fields():  # type: ignore[attr-defined]
                if getattr(f, "is_relation", False) and getattr(
                    f, "many_to_one", False
                ):
                    if getattr(f, "related_model", None) is Lead:
                        qs = Interaction.objects.filter(**{f.name: lead})
                        try:
                            return qs.order_by("-id")
                        except Exception:
                            return qs
        except Exception:
            return Interaction.objects.none()
    return []


def lead_list(request):
    leads = Lead.objects.all().order_by("-created_at")
    return render(request, "crm/lead_list.html", {"leads": leads})


def lead_detail(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    interactions = _lead_interactions(lead)
    opportunity = Opportunity.objects.filter(lead=lead).first()
    return render(
        request,
        "crm/lead_detail.html",
        {"lead": lead, "interactions": interactions, "opportunity": opportunity},
    )


def add_interaction(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if request.method == "POST":
        form = InteractionForm(request.POST)
        if form.is_valid():
            interaction = form.save(commit=False)
            interaction.lead = lead
            # بعض المشاريع قد لا تملك علاقة employee على user
            if hasattr(request.user, "employee"):
                interaction.by = request.user.employee  # type: ignore[attr-defined]
            interaction.save()
            return redirect("crm:lead_detail", pk=pk)
    else:
        form = InteractionForm()
    return render(request, "crm/add_interaction.html", {"form": form, "lead": lead})


def add_opportunity(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if request.method == "POST":
        form = OpportunityForm(request.POST)
        if form.is_valid():
            opp = form.save(commit=False)
            opp.lead = lead
            opp.save()
            return redirect("crm:lead_detail", pk=pk)
    else:
        form = OpportunityForm()
    return render(request, "crm/add_opportunity.html", {"form": form, "lead": lead})


def index(request):
    return render(request, "crm/index.html")


def app_home(request):
    return render(request, "apps/crm/home.html", {"app": "crm"})

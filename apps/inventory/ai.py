# ERP_CORE/inventory/ai.py
from __future__ import annotations

import logging
import math
import statistics
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import (Any, Dict, Iterable, List, Mapping, Optional, Sequence,
                    Tuple)

from django.apps import apps
from django.db.models import F, Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

LOG = logging.getLogger("inventory.ai")

# ========= Optional integrations (guarded imports) =========
try:
    AIDecisionAlert = apps.get_model("ai_decision", "AIDecisionAlert")
except Exception:
    AIDecisionAlert = None  # type: ignore

try:
    RiskIncident = apps.get_model("internal_monitoring", "RiskIncident")
except Exception:
    RiskIncident = None  # type: ignore


# ========= Data DTOs =========
@dataclass(frozen=True)
class DemandPoint:
    day: date
    quantity: float


@dataclass(frozen=True)
class ForecastResult:
    method: str
    horizon_days: int
    daily_forecast: float
    details: Mapping[str, Any]


@dataclass(frozen=True)
class ReorderAdvice:
    sku: str
    current_qty: float
    reorder_point: float
    safety_stock: float
    recommended_order_qty: float
    method: str
    notes: str = ""


@dataclass(frozen=True)
class Anomaly:
    sku: str
    when: datetime
    observed: float
    expected: float
    z_score: float
    level: str  # LOW/MEDIUM/HIGH


# ========= Core math utilities =========
_Z_TABLE: Mapping[float, float] = {
    0.90: 1.2816,
    0.95: 1.6449,
    0.97: 1.8808,
    0.98: 2.0537,
    0.99: 2.3263,
}


def _z_for_service(service: float) -> float:
    service = max(0.90, min(0.99, service))
    # nearest available key
    return min(_Z_TABLE.items(), key=lambda kv: abs(kv[0] - service))[1]


def _safe_mean(values: Sequence[float], default: float = 0.0) -> float:
    vals = [v for v in values if isinstance(v, (int, float))]
    return statistics.mean(vals) if vals else default


def _safe_std(values: Sequence[float], default: float = 0.0) -> float:
    vals = [v for v in values if isinstance(v, (int, float))]
    if len(vals) < 2:
        return default
    try:
        return statistics.stdev(vals)
    except statistics.StatisticsError:
        return default


def _days_between(a: date, b: date) -> int:
    return abs((b - a).days) or 1


# ========= AI/Analytics service =========
class InventoryAIService:
    """
    Enterprise-grade inventory analytics:
    - Demand forecasting (MA/SES).
    - EOQ, Safety Stock, Reorder Point.
    - Anomaly detection on movements (z-score).
    - Optional: raise AI alerts and risk incidents.
    """

    def __init__(
        self,
        item_model: Optional[Any] = None,
        movement_model: Optional[Any] = None,
        sku_field: str = "code",
        qty_field: str = "quantity",
        movement_type_field: str = "movement_type",
        movement_date_field: str = "date",
        movement_item_fk: str = "item",
        incoming_types: Sequence[str] = ("in", "IN", "receipt"),
        outgoing_types: Sequence[str] = ("out", "OUT", "issue", "sale"),
    ) -> None:
        self.Item = item_model or apps.get_model("inventory", "InventoryItem")
        self.Movement = movement_model or apps.get_model(
            "inventory", "InventoryMovement"
        )
        self.sku_field = sku_field
        self.qty_field = qty_field
        self.movement_type_field = movement_type_field
        self.movement_date_field = movement_date_field
        self.movement_item_fk = movement_item_fk
        self._incoming = set(incoming_types)
        self._outgoing = set(outgoing_types)

    # ----- Data access helpers -----
    def list_skus(self) -> List[str]:
        if not self.Item:
            return []
        try:
            qs = self.Item.objects.values_list(self.sku_field, flat=True).distinct()
            return [str(s) for s in qs if s]
        except Exception as exc:
            LOG.warning("Failed to list SKUs: %s", exc)
            return []

    def current_qty(self, sku: str) -> float:
        if not self.Item:
            return 0.0
        try:
            item = (
                self.Item.objects.filter(**{self.sku_field: sku})
                .only("id", "quantity")
                .first()
            )
            return float(getattr(item, "quantity", 0.0) or 0.0) if item else 0.0
        except Exception:
            return 0.0

    def demand_history(
        self, sku: str, days: int = 90, include_returns: bool = False
    ) -> List[DemandPoint]:
        """
        Return daily outgoing quantities for the past `days`.
        If include_returns is False, ignore incoming/returns.
        """
        if not self.Movement or not sku:
            return []
        try:
            item = self.Item.objects.filter(**{self.sku_field: sku}).only("id").first()
            if not item:
                return []
            since = timezone.now().date() - timedelta(days=days)
            qs = (
                self.Movement.objects.filter(**{f"{self.movement_item_fk}": item})
                .filter(**{f"{self.movement_date_field}__date__gte": since})
                .values(self.movement_date_field, self.movement_type_field)
                .annotate(total=Sum(self.qty_field))
                .order_by(self.movement_date_field)
            )
            daily: Dict[date, float] = {}
            for row in qs:
                dt = getattr(row[self.movement_date_field], "date", lambda: None)()
                if not isinstance(dt, date):
                    # handle already-a-date case
                    dt = row[self.movement_date_field]
                qty = float(row.get("total") or 0.0)
                mtype = str(row.get(self.movement_type_field, "")).lower()
                if mtype in self._outgoing:
                    daily[dt] = daily.get(dt, 0.0) + max(0.0, qty)
                elif include_returns and mtype in self._incoming:
                    daily[dt] = daily.get(dt, 0.0) - max(0.0, qty)
            # fill missing days with 0 to keep horizon stable
            result: List[DemandPoint] = []
            for i in range(days):
                d = since + timedelta(days=i)
                result.append(DemandPoint(d, daily.get(d, 0.0)))
            return result
        except Exception as exc:
            LOG.warning("Failed to fetch demand history for %s: %s", sku, exc)
            return []

    # ----- Forecasting -----
    def forecast_moving_average(
        self, history: Sequence[DemandPoint], window: int = 14
    ) -> ForecastResult:
        window = max(1, min(window, len(history) or 1))
        vals = [p.quantity for p in history[-window:]]
        avg = _safe_mean(vals, 0.0)
        return ForecastResult(
            method=f"MA({window})",
            horizon_days=1,
            daily_forecast=avg,
            details={"window": window, "mean": avg, "n": len(vals)},
        )

    def forecast_ses(
        self, history: Sequence[DemandPoint], alpha: float = 0.3
    ) -> ForecastResult:
        alpha = max(0.01, min(0.99, alpha))
        vals = [p.quantity for p in history if isinstance(p.quantity, (int, float))]
        if not vals:
            return ForecastResult("SES", 1, 0.0, {"alpha": alpha})
        s = vals[0]
        for x in vals[1:]:
            s = alpha * x + (1.0 - alpha) * s
        return ForecastResult("SES", 1, s, {"alpha": alpha, "last_level": s})

    # ----- EOQ / Safety Stock / ROP -----
    def eoq(
        self, annual_demand: float, order_cost: float, holding_cost_per_unit: float
    ) -> float:
        try:
            if annual_demand <= 0 or order_cost <= 0 or holding_cost_per_unit <= 0:
                return 0.0
            q = math.sqrt(2.0 * annual_demand * order_cost / holding_cost_per_unit)
            return float(q)
        except Exception:
            return 0.0

    def safety_stock(
        self,
        daily_demand_std: float,
        lead_time_days: float,
        service_level: float = 0.95,
        lead_time_std: Optional[float] = None,
    ) -> float:
        """
        SS ~ z * sigma_LT. If lead_time_std not provided, assumes demand variability only:
        sigma_LT = daily_demand_std * sqrt(LT).
        Otherwise sigma_LT = sqrt( (daily_demand_std^2 * LT) + (mean_demand^2 * lead_time_std^2) )
        (we don't know mean_demand here; use conservative first term only if mean unknown).
        """
        z = _z_for_service(service_level)
        lt = max(0.0, lead_time_days)
        if lt <= 0.0:
            return 0.0
        sigma_lt = daily_demand_std * math.sqrt(lt)
        if lead_time_std and lead_time_std > 0:
            # could incorporate mean demand term if available; we keep conservative estimate.
            sigma_lt = math.sqrt(
                (daily_demand_std**2) * lt + (0.0 * (lead_time_std**2))
            )
        return max(0.0, z * sigma_lt)

    def reorder_point(
        self,
        daily_demand_mean: float,
        lead_time_days: float,
        safety_stock_qty: float,
    ) -> float:
        return max(
            0.0,
            daily_demand_mean * max(0.0, lead_time_days) + max(0.0, safety_stock_qty),
        )

    # ----- Turn-key recommendation -----
    def recommend_for_sku(
        self,
        sku: str,
        *,
        lookback_days: int = 90,
        forecast_method: str = "SES",
        alpha: float = 0.3,
        window: int = 14,
        lead_time_days: float = 7.0,
        service_level: float = 0.95,
        annual_order_cost: float = 25.0,
        annual_holding_cost_per_unit: float = 1.5,
        min_order_qty: float = 0.0,
    ) -> Optional[ReorderAdvice]:
        hist = self.demand_history(sku, days=lookback_days)
        if not hist:
            return None

        # compute stats
        daily_vals = [p.quantity for p in hist]
        mean = _safe_mean(daily_vals, 0.0)
        std = _safe_std(daily_vals, 0.0)

        if forecast_method.upper() == "MA":
            fc = self.forecast_moving_average(hist, window=window)
        else:
            fc = self.forecast_ses(hist, alpha=alpha)
        daily_fc = fc.daily_forecast or mean

        ss = self.safety_stock(
            std, lead_time_days=lead_time_days, service_level=service_level
        )
        rop = self.reorder_point(
            daily_fc, lead_time_days=lead_time_days, safety_stock_qty=ss
        )

        # EOQ using rough annualized demand
        annual_demand = max(0.0, daily_fc) * 365.0
        eoq_qty = self.eoq(
            annual_demand, annual_order_cost, annual_holding_cost_per_unit
        )

        current = self.current_qty(sku)
        rec_order = 0.0
        if current <= rop:
            rec_order = max(eoq_qty, min_order_qty)

        return ReorderAdvice(
            sku=sku,
            current_qty=current,
            reorder_point=round(rop, 3),
            safety_stock=round(ss, 3),
            recommended_order_qty=round(rec_order, 3),
            method=fc.method,
            notes=_("Mean={mean:.2f}, Std={std:.2f}, DailyFc={fc:.2f}").format(
                mean=mean, std=std, fc=daily_fc
            ),
        )

    # ----- Anomaly detection -----
    def detect_anomalies(
        self,
        sku: str,
        *,
        lookback_days: int = 60,
        z_threshold: float = 3.0,
    ) -> List[Anomaly]:
        hist = self.demand_history(sku, days=lookback_days)
        if not hist:
            return []
        vals = [p.quantity for p in hist]
        mu = _safe_mean(vals, 0.0)
        sigma = _safe_std(vals, 0.0)
        if sigma <= 0.0:
            return []

        anomalies: List[Anomaly] = []
        for p in hist:
            z = (p.quantity - mu) / sigma if sigma else 0.0
            if abs(z) >= z_threshold:
                when_dt = datetime.combine(p.day, datetime.min.time()).replace(
                    tzinfo=timezone.get_current_timezone()
                )
                level = "HIGH" if abs(z) >= 4 else "MEDIUM"
                anomalies.append(
                    Anomaly(
                        sku=sku,
                        when=when_dt,
                        observed=p.quantity,
                        expected=mu,
                        z_score=z,
                        level=level,
                    )
                )
        return anomalies

    # ----- Alerts/Incidents hooks -----
    def emit_ai_alert(
        self, section: str, alert_type: str, message: str, level: str = "info"
    ) -> None:
        if AIDecisionAlert is None:
            return
        try:
            AIDecisionAlert.objects.create(
                section=section,
                alert_type=alert_type,
                message=message,
                level=level,
            )
        except Exception as exc:
            LOG.warning("Failed to create AIDecisionAlert: %s", exc)

    def emit_risk_incident(
        self, category: str, event_type: str, risk_level: str, notes: str
    ) -> None:
        if RiskIncident is None:
            return
        try:
            RiskIncident.objects.create(
                user=None,
                category=category,
                event_type=event_type,
                risk_level=risk_level,
                notes=notes,
            )
        except Exception as exc:
            LOG.warning("Failed to create RiskIncident: %s", exc)

    # ----- Convenience batch API -----
    def batch_recommendations(
        self,
        *,
        skus: Optional[Iterable[str]] = None,
        **kwargs: Any,
    ) -> List[ReorderAdvice]:
        items = list(skus) if skus else self.list_skus()
        out: List[ReorderAdvice] = []
        for sku in items:
            try:
                rec = self.recommend_for_sku(sku, **kwargs)
                if rec:
                    out.append(rec)
            except Exception as exc:
                LOG.warning("Recommendation failed for %s: %s", sku, exc)
        return out

    def scan_and_alert_anomalies(
        self,
        *,
        skus: Optional[Iterable[str]] = None,
        lookback_days: int = 60,
        z_threshold: float = 3.0,
    ) -> List[Anomaly]:
        items = list(skus) if skus else self.list_skus()
        anomalies: List[Anomaly] = []
        for sku in items:
            try:
                anoms = self.detect_anomalies(
                    sku, lookback_days=lookback_days, z_threshold=z_threshold
                )
                for a in anoms:
                    msg = _(
                        "Anomaly for {sku} on {day}: observed={obs}, expected≈{exp}, z={z}"
                    ).format(
                        sku=sku,
                        day=a.when.date().isoformat(),
                        obs=a.observed,
                        exp=round(a.expected, 2),
                        z=round(a.z_score, 2),
                    )
                    self.emit_ai_alert("inventory", "anomaly", msg, level="warning")
                    self.emit_risk_incident("Stock", "Demand anomaly", "MEDIUM", msg)
                anomalies.extend(anoms)
            except Exception as exc:
                LOG.warning("Anomaly scan failed for %s: %s", sku, exc)
        return anomalies


# ========= Top-level convenience functions =========
_service_singleton: Optional[InventoryAIService] = None


def get_service() -> InventoryAIService:
    global _service_singleton
    if _service_singleton is None:
        _service_singleton = InventoryAIService()
    return _service_singleton


def forecast_for_sku(
    sku: str,
    *,
    method: str = "SES",
    lookback_days: int = 90,
    alpha: float = 0.3,
    window: int = 14,
) -> ForecastResult:
    svc = get_service()
    hist = svc.demand_history(sku, days=lookback_days)
    if method.upper() == "MA":
        return svc.forecast_moving_average(hist, window=window)
    return svc.forecast_ses(hist, alpha=alpha)


def advise_reorder(
    sku: str,
    *,
    lead_time_days: float = 7.0,
    service_level: float = 0.95,
    min_order_qty: float = 0.0,
) -> Optional[ReorderAdvice]:
    svc = get_service()
    return svc.recommend_for_sku(
        sku,
        lead_time_days=lead_time_days,
        service_level=service_level,
        min_order_qty=min_order_qty,
    )


def scan_anomalies(
    *,
    skus: Optional[Iterable[str]] = None,
    lookback_days: int = 60,
    z_threshold: float = 3.0,
) -> List[Anomaly]:
    svc = get_service()
    return svc.scan_and_alert_anomalies(
        skus=skus, lookback_days=lookback_days, z_threshold=z_threshold
    )

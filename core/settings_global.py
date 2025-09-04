# ERP_CORE/core/settings_global.py
# Global Expansion Settings — Multi-Company, Multi-Currency, Approvals, Audit, Advanced Ops
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Dict, List, Set, TypedDict, Union

# ── Typed structures (for mypy clarity) ─────────────────────────────────────────


class CompanyInfo(TypedDict):
    name: str
    timezone: str
    locale: str


class CurrencyInfo(TypedDict, total=False):
    symbol: str
    decimals: int


class AuditSink(TypedDict):
    backend: str  # db | log | both | custom
    channel: str


# ── Multi-Company ──────────────────────────────
ENABLE_MULTI_COMPANY: bool = True
DEFAULT_COMPANY_CODE: str = "MAIN"
COMPANIES: Dict[str, CompanyInfo] = {
    "MAIN": {"name": "Main Company", "timezone": "Africa/Cairo", "locale": "ar"},
    "INTL": {"name": "International Holding", "timezone": "UTC", "locale": "en"},
}
COMPANY_HEADER_KEY: str = "HTTP_X_COMPANY"
COMPANY_SESSION_KEY: str = "company_code"
COMPANY_SUBDOMAIN_ENABLED: bool = False

# ── Multi-Currency ─────────────────────────────
ENABLE_MULTI_CURRENCY: bool = True
DEFAULT_CURRENCY: str = "EGP"
SUPPORTED_CURRENCIES: Dict[str, CurrencyInfo] = {
    "EGP": {"symbol": "E£", "decimals": 2},
    "USD": {"symbol": "$", "decimals": 2},
    "EUR": {"symbol": "€", "decimals": 2},
    "SAR": {"symbol": "﷼", "decimals": 2},
    "AED": {"symbol": "د.إ", "decimals": 2},
}
FX_PROVIDER: str = "manual"
FX_CACHE_TTL_SECONDS: int = 3600
CURRENCY_SESSION_KEY: str = "currency_code"
CURRENCY_HEADER_KEY: str = "HTTP_X_CURRENCY"

# ── Approvals ──────────────────────────────────
APPROVALS_ENABLED: bool = True
APPROVAL_LEVELS: Dict[str, List[str]] = {
    "purchases": ["initiator", "supervisor", "finance", "director"],
    "payments": ["initiator", "finance", "cfo"],
    "documents": ["owner", "reviewer", "approver"],
}
APPROVAL_ROLE_ALIASES: Dict[str, str] = {
    "initiator": "Requester",
    "supervisor": "Supervisor",
    "finance": "Finance",
    "cfo": "CFO",
    "director": "Director",
    "owner": "Owner",
    "reviewer": "Reviewer",
    "approver": "Approver",
}

# ── Audit Trails ───────────────────────────────
AUDIT_TRAIL_ENABLED: bool = True
AUDIT_SINK: AuditSink = {
    "backend": "db",  # db | log | both | custom
    "channel": "audit",
}
AUDIT_MASK_FIELDS: Set[str] = {
    "password",
    "token",
    "secret",
    "api_key",
    "authorization",
}

# ── Advanced Ops flags ─────────────────────────
ENABLE_WMS_ADVANCED: bool = True
ENABLE_MRP_ADVANCED: bool = True
ENABLE_QMS_ADVANCED: bool = True

# ── Template / Context exposure key ────────────
GLOBAL_CONTEXT_KEY: str = "global_ctx"


# ── Helpers ────────────────────────────────────
def currency_symbol(code: str) -> str:
    """
    Return currency symbol for the given ISO code; fallback to code if unknown.
    """
    return SUPPORTED_CURRENCIES.get(code, {}).get("symbol", code)


def currency_decimals(code: str) -> int:
    """
    Return number of decimal places for currency code; default to 2 on unknown/invalid.
    """
    val = SUPPORTED_CURRENCIES.get(code, {}).get("decimals", 2)
    try:
        return int(val) if val is not None else 2
    except (ValueError, TypeError):
        return 2


_NumberLike = Union[Decimal, int, float, str]


def _to_decimal(value: _NumberLike) -> Decimal:
    """
    Safely convert a numeric-like value to Decimal.

    - Uses str() for float to avoid binary FP artifacts.
    - Re-raises InvalidOperation as ValueError for cleaner call sites.
    """
    if isinstance(value, Decimal):
        return value
    try:
        if isinstance(value, float):
            return Decimal(str(value))
        return Decimal(value)
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"Invalid numeric value for Decimal: {value!r}") from exc


def money_round(amount: _NumberLike, code: str) -> Decimal:
    """
    Quantize amount to the currency's decimal precision.

    Examples:
        >>> money_round(10.123, "USD")
        Decimal('10.12')
        >>> money_round("99.999", "EGP")
        Decimal('100.00')
    """
    q = Decimal(10) ** -currency_decimals(code)
    return _to_decimal(amount).quantize(q)

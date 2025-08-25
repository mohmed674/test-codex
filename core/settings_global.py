# ERP_CORE/core/settings_global.py
# Global Expansion Settings — Multi-Company, Multi-Currency, Approvals, Audit, Advanced Ops
from decimal import Decimal

# ── Multi-Company ──────────────────────────────
ENABLE_MULTI_COMPANY: bool = True
DEFAULT_COMPANY_CODE: str = "MAIN"
COMPANIES: dict = {
    "MAIN": {"name": "Main Company", "timezone": "Africa/Cairo", "locale": "ar"},
    "INTL": {"name": "International Holding", "timezone": "UTC", "locale": "en"},
}
COMPANY_HEADER_KEY: str = "HTTP_X_COMPANY"
COMPANY_SESSION_KEY: str = "company_code"
COMPANY_SUBDOMAIN_ENABLED: bool = False

# ── Multi-Currency ─────────────────────────────
ENABLE_MULTI_CURRENCY: bool = True
DEFAULT_CURRENCY: str = "EGP"
SUPPORTED_CURRENCIES: dict = {
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
APPROVAL_LEVELS: dict = {
    "purchases": ["initiator", "supervisor", "finance", "director"],
    "payments": ["initiator", "finance", "cfo"],
    "documents": ["owner", "reviewer", "approver"],
}
APPROVAL_ROLE_ALIASES: dict = {
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
AUDIT_SINK: dict = {
    "backend": "db",   # db | log | both | custom
    "channel": "audit",
}
AUDIT_MASK_FIELDS = {"password", "token", "secret", "api_key", "authorization"}

# ── Advanced Ops flags ─────────────────────────
ENABLE_WMS_ADVANCED: bool = True
ENABLE_MRP_ADVANCED: bool = True
ENABLE_QMS_ADVANCED: bool = True

# ── Template / Context exposure key ────────────
GLOBAL_CONTEXT_KEY: str = "global_ctx"

# ── Helpers ────────────────────────────────────
def currency_symbol(code: str) -> str:
    return SUPPORTED_CURRENCIES.get(code, {}).get("symbol", code)

def currency_decimals(code: str) -> int:
    return int(SUPPORTED_CURRENCIES.get(code, {}).get("decimals", 2))

def money_round(amount, code: str) -> Decimal:
    q = Decimal(10) ** -currency_decimals(code)
    return Decimal(amount).quantize(q)

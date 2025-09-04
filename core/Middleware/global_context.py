# core/middleware/global_context.py
# Middleware + Context Processor for Global Expansion
from typing import Any, Callable, Dict

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.utils import translation


def _s(name: str, default: Any) -> Any:
    return getattr(settings, name, default)


ENABLE_MULTI_COMPANY: bool = _s("ENABLE_MULTI_COMPANY", True)
DEFAULT_COMPANY_CODE: str = _s("DEFAULT_COMPANY_CODE", "MAIN")
COMPANIES: Dict[str, Dict[str, Any]] = _s(
    "COMPANIES", {"MAIN": {"name": "Main Company", "timezone": "UTC", "locale": "en"}}
)
COMPANY_HEADER_KEY: str = _s("COMPANY_HEADER_KEY", "HTTP_X_COMPANY")
COMPANY_SESSION_KEY: str = _s("COMPANY_SESSION_KEY", "company_code")

ENABLE_MULTI_CURRENCY: bool = _s("ENABLE_MULTI_CURRENCY", True)
DEFAULT_CURRENCY: str = _s("DEFAULT_CURRENCY", "EGP")
SUPPORTED_CURRENCIES: Dict[str, Dict[str, Any]] = _s(
    "SUPPORTED_CURRENCIES", {"EGP": {"symbol": "E£", "decimals": 2}}
)
CURRENCY_HEADER_KEY: str = _s("CURRENCY_HEADER_KEY", "HTTP_X_CURRENCY")
CURRENCY_SESSION_KEY: str = _s("CURRENCY_SESSION_KEY", "currency_code")

GLOBAL_CONTEXT_KEY: str = _s("GLOBAL_CONTEXT_KEY", "global_ctx")


def _pick_company(request: HttpRequest) -> str:
    return (
        request.META.get(COMPANY_HEADER_KEY)
        or request.session.get(COMPANY_SESSION_KEY)
        or DEFAULT_COMPANY_CODE
    )


def _pick_currency(request: HttpRequest) -> str:
    return (
        request.META.get(CURRENCY_HEADER_KEY)
        or request.session.get(CURRENCY_SESSION_KEY)
        or DEFAULT_CURRENCY
    )


class GlobalContextMiddleware:
    """
    Injects:
      - request.company_code / request.company
      - request.currency_code
      - request.global_ctx
    Also activates translation locale from company.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        company_code = _pick_company(request)
        if company_code not in COMPANIES:
            company_code = DEFAULT_COMPANY_CODE

        currency_code = _pick_currency(request)
        if currency_code not in SUPPORTED_CURRENCIES:
            currency_code = DEFAULT_CURRENCY

        company: Dict[str, Any] = {
            "code": company_code,
            "name": COMPANIES.get(company_code, {}).get("name", company_code),
            "timezone": COMPANIES.get(company_code, {}).get("timezone", "UTC"),
            "locale": COMPANIES.get(company_code, {}).get("locale", "en"),
        }

        request.company_code = company_code  # type: ignore[attr-defined]
        request.currency_code = currency_code  # type: ignore[attr-defined]
        request.company = company  # type: ignore[attr-defined]

        request.global_ctx = {  # type: ignore[attr-defined]
            "company": company,
            "currency": {
                "code": currency_code,
                "symbol": SUPPORTED_CURRENCIES.get(currency_code, {}).get(
                    "symbol", currency_code
                ),
                "decimals": SUPPORTED_CURRENCIES.get(currency_code, {}).get(
                    "decimals", 2
                ),
            },
            "features": {
                "multi_company": ENABLE_MULTI_COMPANY,
                "multi_currency": ENABLE_MULTI_CURRENCY,
                "approvals": getattr(settings, "APPROVALS_ENABLED", True),
                "audit_trail": getattr(settings, "AUDIT_TRAIL_ENABLED", True),
                "wms_advanced": getattr(settings, "ENABLE_WMS_ADVANCED", True),
                "mrp_advanced": getattr(settings, "ENABLE_MRP_ADVANCED", True),
                "qms_advanced": getattr(settings, "ENABLE_QMS_ADVANCED", True),
            },
        }

        try:
            translation.activate(company["locale"])
            request.LANGUAGE_CODE = company["locale"]  # type: ignore[attr-defined]
        except Exception:
            pass

        return self.get_response(request)


def global_context_processor(request: HttpRequest) -> Dict[str, Any]:
    """Expose global context to templates as {{ global_ctx }}"""
    return {GLOBAL_CONTEXT_KEY: getattr(request, "global_ctx", {})}

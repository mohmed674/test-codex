# apps/banking/services/provider_service.py

from __future__ import annotations

import logging
from typing import Any

from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.banking.models import BankProvider

logger = logging.getLogger(__name__)


class ProviderService:
    """
    Service layer for managing BankProvider logic.
    """

    @staticmethod
    def create(data: dict[str, Any]) -> BankProvider:
        with transaction.atomic():
            provider = BankProvider.objects.create(
                name=str(data.get("name") or "").strip(),
                code=str(data.get("code") or "").strip(),
            )
            logger.info("Created BankProvider: %s (%s)", provider.name, provider.code)
            return provider

    @staticmethod
    def update(pk: int, data: dict[str, Any]) -> BankProvider:
        provider = get_object_or_404(BankProvider, pk=pk)
        provider.name = str(data.get("name") or provider.name).strip()
        provider.code = str(data.get("code") or provider.code).strip()
        with transaction.atomic():
            provider.save()
            logger.info("Updated BankProvider: %s (%s)", provider.name, provider.code)
            return provider

    @staticmethod
    def delete(pk: int) -> None:
        provider = get_object_or_404(BankProvider, pk=pk)
        logger.warning("Deleting BankProvider: %s (%s)", provider.name, provider.code)
        with transaction.atomic():
            provider.delete()

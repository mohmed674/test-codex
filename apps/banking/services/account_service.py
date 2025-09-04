# apps/banking/services/account_service.py

from __future__ import annotations

import logging
from typing import Any

from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.banking.models import BankAccount

logger = logging.getLogger(__name__)


class AccountService:
    """
    Service layer for managing BankAccount logic.
    """

    @staticmethod
    def create(data: dict[str, Any]) -> BankAccount:
        with transaction.atomic():
            account = BankAccount.objects.create(
                provider_id=data.get("provider"),
                name=str(data.get("name") or "").strip(),
                account_number=str(data.get("account_number") or "").strip(),
                currency=str(data.get("currency") or "").strip(),
            )
            logger.info(
                "Created BankAccount: %s (%s)", account.name, account.account_number
            )
            return account

    @staticmethod
    def update(pk: int, data: dict[str, Any]) -> BankAccount:
        account = get_object_or_404(BankAccount, pk=pk)
        account.name = str(data.get("name") or account.name).strip()
        account.account_number = str(
            data.get("account_number") or account.account_number
        ).strip()
        account.currency = str(data.get("currency") or account.currency).strip()
        with transaction.atomic():
            account.save()
            logger.info(
                "Updated BankAccount: %s (%s)", account.name, account.account_number
            )
            return account

    @staticmethod
    def delete(pk: int) -> None:
        account = get_object_or_404(BankAccount, pk=pk)
        logger.warning(
            "Deleting BankAccount: %s (%s)", account.name, account.account_number
        )
        with transaction.atomic():
            account.delete()

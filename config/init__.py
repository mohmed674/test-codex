# ERP_CORE/ERP_CORE/__init__.py
# pyright: reportMissingImports=false, reportUnusedImport=false
from ERP_CORE.celery_app import app as celery_app  # noqa: F401

__all__ = ("celery_app",)

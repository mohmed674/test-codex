# core/management/commands/smoke_apps.py
# -*- coding: utf-8 -*-
"""
Quick smoke test for /<app>/ routes for all apps under apps/.
Non-destructive diagnostic command; does not modify data.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, List, Sequence

from django.conf import settings
from django.core.management.base import BaseCommand
from django.test import Client
from django.utils.translation import gettext_lazy as _


class Command(BaseCommand):
    help = _("فحص سريع لمسارات /<app>/ لكل التطبيقات داخل apps/.")

    def add_arguments(self, parser) -> None:
        parser.add_argument("--only", nargs="*", help=_("حدد أسماء تطبيقات معينة فقط"))
        parser.add_argument(
            "--strict",
            action="store_true",
            help=_("اعتبر 302 كتحويل وليس نجاح"),
        )

    def handle(self, *args: str, **opts: Any) -> None:
        base: Path = Path(settings.BASE_DIR)
        apps_dir: Path = base / "apps"
        client = Client()

        if not apps_dir.exists():
            self.stderr.write(self.style.ERROR(_("❌ لم يتم العثور على مجلد apps/")))
            return

        targets: List[str] = [
            p.name
            for p in sorted(apps_dir.iterdir(), key=lambda q: q.name.lower())
            if p.is_dir() and not p.name.startswith("__")
        ]
        only: Sequence[str] | None = opts.get("only")
        if only:
            only_set = set(only)
            targets = [t for t in targets if t in only_set]

        ok: List[str] = []
        redirects: List[str] = []
        not_found: List[str] = []
        errors: List[str] = []

        self.stdout.write(_("🚦 بدء الفحص السريع لمسارات التطبيقات...\n"))

        for app in targets:
            url = f"/{app}/"
            try:
                resp = client.get(url, follow=False)
                code = resp.status_code
                if 200 <= code < 300:
                    ok.append(app)
                elif code in (301, 302, 303, 307, 308):
                    redirects.append(app)
                elif code == 404:
                    not_found.append(app)
                else:
                    errors.append(f"{app}:{code}")
            except (
                Exception
            ) as e:  # Intentionally broad to record loader/runtime issues per app
                errors.append(f"{app}:EXC:{e.__class__.__name__}")

        # Non-strict mode treats redirects as OK since many pages are protected
        treat_redirects_as_ok: bool = not opts.get("strict", False)
        if treat_redirects_as_ok:
            ok = sorted(set(ok) | set(redirects))
            redirects = []

        self.stdout.write("\n================= SMOKE RESULT =================")
        ok_line = f"✅ OK    ({len(ok)}): " + (", ".join(sorted(ok)) or _("لا يوجد"))
        self.stdout.write(self.style.SUCCESS(ok_line))

        if redirects:
            red_line = f"↪️  Redirects ({len(redirects)}): " + (
                ", ".join(sorted(redirects)) or _("لا يوجد")
            )
            self.stdout.write(self.style.HTTP_INFO(red_line))

        nf_line = f"⚠️  404  ({len(not_found)}): " + (
            ", ".join(sorted(not_found)) or _("لا يوجد")
        )
        self.stdout.write(self.style.WARNING(nf_line))

        err_line = f"❌ ERR   ({len(errors)}): " + (", ".join(errors) or _("لا يوجد"))
        self.stdout.write(self.style.ERROR(err_line))

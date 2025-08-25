# core/management/commands/smoke_apps.py
# -*- coding: utf-8 -*-
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand
from django.test import Client

class Command(BaseCommand):
    help = "فحص سريع لمسارات /<app>/ لكل التطبيقات داخل apps/."

    def add_arguments(self, parser):
        parser.add_argument("--only", nargs="*", help="حدد أسماء تطبيقات معينة فقط")
        parser.add_argument("--strict", action="store_true", help="اعتبر 302 كتحويل وليس نجاح")

    def handle(self, *args, **opts):
        base = Path(getattr(settings, "BASE_DIR"))
        apps_dir = base / "apps"
        client = Client()

        if not apps_dir.exists():
            self.stderr.write(self.style.ERROR("❌ لم يتم العثور على مجلد apps/"))
            return

        targets = [p.name for p in sorted(apps_dir.iterdir()) if p.is_dir() and not p.name.startswith("__")]
        only = opts.get("only")
        if only:
            targets = [t for t in targets if t in set(only)]

        ok, redirects, not_found, errors = [], [], [], []
        self.stdout.write("🚦 بدء الفحص السريع لمسارات التطبيقات...\n")

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
            except Exception as e:
                errors.append(f"{app}:EXC:{e.__class__.__name__}")

        # في الوضع غير الصارم، نعتبر 302 نجاح لأن أغلب الصفحات محمية
        treat_redirects_as_ok = not opts.get("strict", False)
        if treat_redirects_as_ok:
            ok = sorted(set(ok) | set(redirects))
            redirects = []

        self.stdout.write("\n================= SMOKE RESULT =================")
        self.stdout.write(self.style.SUCCESS(f"✅ OK    ({len(ok)}): " + (", ".join(sorted(ok)) or "لا يوجد")))
        if redirects:
            self.stdout.write(self.style.HTTP_INFO(f"↪️  Redirects ({len(redirects)}): " + (", ".join(sorted(redirects)) or "لا يوجد")))
        self.stdout.write(self.style.WARNING(f"⚠️  404  ({len(not_found)}): " + (", ".join(sorted(not_found)) or "لا يوجد")))
        self.stdout.write(self.style.ERROR(f"❌ ERR   ({len(errors)}): " + (", ".join(errors) or "لا يوجد")))

# core/management/commands/prepare_db.py
# -*- coding: utf-8 -*-
import sys
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

class Command(BaseCommand):
    help = "تهيئة قاعدة البيانات: makemigrations + migrate بالترتيب الصحيح."

    def add_arguments(self, parser):
        parser.add_argument("--fake-initial", action="store_true", help="تمرير --fake-initial للـ migrate")

    def handle(self, *args, **opts):
        try:
            self.stdout.write(self.style.HTTP_INFO("🔧 makemigrations..."))
            call_command("makemigrations", interactive=False, verbosity=1)

            self.stdout.write(self.style.HTTP_INFO("📦 migrate..."))
            mig_opts = {"verbosity": 1}
            if opts.get("fake_initial"):
                mig_opts["fake_initial"] = True
            call_command("migrate", **mig_opts)

            self.stdout.write(self.style.SUCCESS("✅ قاعدة البيانات جاهزة."))
        except Exception as e:
            raise CommandError(str(e))

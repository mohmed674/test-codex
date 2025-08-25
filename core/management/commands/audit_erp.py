import csv, os
from django.core.management.base import BaseCommand
from django.apps import apps as django_apps
from django.urls import get_resolver

class Command(BaseCommand):
    help = "Export ERP audit: models, fields, urls, apps"

    def add_arguments(self, parser):
        parser.add_argument("--outdir", default="audit_out", help="Output directory")

    def handle(self, *args, **opts):
        outdir = opts["outdir"]
        os.makedirs(outdir, exist_ok=True)

        # 1) Apps
        apps_csv = os.path.join(outdir, "apps.csv")
        with open(apps_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["app_label","path"])
            for config in sorted(django_apps.get_app_configs(), key=lambda c: c.label):
                w.writerow([config.label, getattr(config, "path", "")])

        # 2) Models + Fields
        models_csv = os.path.join(outdir, "models.csv")
        with open(models_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["app_label","model","field_name","field_type","related_model","null","blank"])
            for model in django_apps.get_models():
                app_label = model._meta.app_label
                model_name = model.__name__
                for field in model._meta.get_fields():
                    try:
                        ftype = field.get_internal_type()
                    except Exception:
                        ftype = type(field).__name__
                    rel = getattr(getattr(field, "remote_field", None), "model", None)
                    rel_label = ""
                    if rel:
                        try:
                            rel_label = f"{rel._meta.app_label}.{rel.__name__}"
                        except Exception:
                            rel_label = str(rel)
                    null = getattr(field, "null", "")
                    blank = getattr(field, "blank", "")
                    w.writerow([app_label, model_name, field.name, ftype, rel_label, null, blank])

        # 3) URLs
        urls_csv = os.path.join(outdir, "urls.csv")
        with open(urls_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["pattern","name","default_kwargs","app_name","namespace"])
            resolver = get_resolver()
            for patt in resolver.url_patterns:
                # drill down recursively
                def walk(pattern, prefix=""):
                    from django.urls.resolvers import URLPattern, URLResolver
                    if isinstance(pattern, URLPattern):
                        w.writerow([prefix + str(pattern.pattern), pattern.name, pattern.default_args, "", ""])
                    elif isinstance(pattern, URLResolver):
                        ns = pattern.namespace or ""
                        appn = getattr(pattern, "app_name", "") or ""
                        for p in pattern.url_patterns:
                            walk(p, prefix + str(pattern.pattern))
                    else:
                        w.writerow([prefix + str(pattern), "", "", "", ""])
                walk(patt)

        self.stdout.write(self.style.SUCCESS(f"Audit exported to: {outdir}"))

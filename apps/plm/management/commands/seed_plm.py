from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from ...models import (
    LifecycleStage,
    ProductTemplate,
    ProductVersion,
    ProductLifecycle,
    PLMDocument,
    Bom,
    BomLine,
    ChangeRequest,
    ChangeRequestItem,
)


def allow(model, data: dict):
    names = {f.attname if hasattr(f, "attname") else f.name for f in model._meta.get_fields()}
    return {k: v for k, v in data.items() if k in names}


class Command(BaseCommand):
    help = "Seed PLM core data (stages, demo products, versions, BOMs, documents, and a sample change request)."

    @transaction.atomic
    def handle(self, *args, **options):
        now = timezone.now().date()

        # ---- Lifecycle Stages ----
        stages_seed = [
            {"name": "Idea",       "order": 1},
            {"name": "Design",     "order": 2},
            {"name": "Prototype",  "order": 3},
            {"name": "Production", "order": 4},
            {"name": "QA",         "order": 5},
            {"name": "Launch",     "order": 6},
            {"name": "EOL",        "order": 7},
        ]
        stages = []
        for row in stages_seed:
            obj, _ = LifecycleStage.objects.get_or_create(
                name=row["name"], defaults=allow(LifecycleStage, row)
            )
            for k, v in allow(LifecycleStage, row).items():
                setattr(obj, k, v)
            obj.save()
            stages.append(obj)

        # ---- Products (Templates) ----
        products_seed = [
            {"name": "T-Shirt X", "code": "TSHIRT-X", "category": "Apparel", "uom": "pcs", "description": "Cotton tee"},
            {"name": "Jeans Pro", "code": "JEANS-PRO","category": "Apparel", "uom": "pcs", "description": "Slim fit denim"},
            {"name": "Sneakers Z","code": "SNKR-Z",   "category": "Footwear","uom": "prs", "description": "Lightweight runner"},
        ]
        products = []
        for row in products_seed:
            obj, _ = ProductTemplate.objects.get_or_create(
                code=row["code"], defaults=allow(ProductTemplate, row)
            )
            for k, v in allow(ProductTemplate, row).items():
                setattr(obj, k, v)
            obj.save()
            products.append(obj)

        # ---- Some material components to use in BOMs ----
        components_seed = [
            {"name": "Cotton Fabric 180gsm", "code": "FAB-COT-180", "category": "Material", "uom": "m"},
            {"name": "Denim 12oz",           "code": "FAB-DEN-12OZ","category": "Material", "uom": "m"},
            {"name": "Poly Thread #40",      "code": "THR-40",      "category": "Accessory","uom": "pcs"},
            {"name": "Rubber Sole",          "code": "SOLE-RBR",    "category": "Material", "uom": "pcs"},
        ]
        components = []
        for row in components_seed:
            comp, _ = ProductTemplate.objects.get_or_create(
                code=row["code"], defaults=allow(ProductTemplate, row)
            )
            for k, v in allow(ProductTemplate, row).items():
                setattr(comp, k, v)
            comp.save()
            components.append(comp)

        # ---- Product Versions (v1.0 approved + active) ----
        versions = {}
        for prod in products:
            v1, _ = ProductVersion.objects.get_or_create(
                product=prod,
                version_code="v1.0",
                defaults=allow(
                    ProductVersion,
                    {
                        "title": f"{prod.name} initial",
                        "status": "approved",
                        "is_active": True,
                        "effective_from": now,
                    },
                ),
            )
            v1.title = v1.title or f"{prod.name} initial"
            v1.status = "approved"
            v1.is_active = True
            v1.effective_from = v1.effective_from or now
            v1.save()
            versions[prod.code] = v1

        # ---- Product Lifecycle timeline ----
        for prod in products:
            for idx, stg in enumerate(stages):
                started_at = timezone.now()
                ended_at = None
                if stg.name in {"Idea", "Design", "Prototype"}:
                    ended_at = timezone.now()
                ProductLifecycle.objects.update_or_create(
                    product=prod, stage=stg,
                    defaults={"started_at": started_at, "ended_at": ended_at}
                )

        # ---- Documents and attach to versions ----
        for prod in products:
            doc, _ = PLMDocument.objects.get_or_create(
                name=f"{prod.name} Tech Pack",
                defaults={"version": "v1.0"},
            )
            v = versions[prod.code]
            v.documents.add(doc)

        # ---- BOMs for each v1.0 ----
        for prod in products:
            v = versions[prod.code]
            bom, _ = Bom.objects.get_or_create(
                product_version=v,
                code="BOM-1",
                defaults={"is_active": True, "notes": f"Starter BOM for {prod.code} v1.0"},
            )
            if bom.lines.exists():
                bom.lines.all().delete()

            if prod.code == "TSHIRT-X":
                lines = [
                    {"component": "FAB-COT-180", "description": "Body panels", "quantity": 1.4, "uom": "m", "order": 1},
                    {"component": "THR-40",      "description": "Sewing thread", "quantity": 1,   "uom": "pcs", "order": 2},
                ]
            elif prod.code == "JEANS-PRO":
                lines = [
                    {"component": "FAB-DEN-12OZ","description": "Main fabric", "quantity": 1.6, "uom": "m", "order": 1},
                    {"component": "THR-40",      "description": "Stitching",   "quantity": 1,   "uom": "pcs","order": 2},
                ]
            else:
                lines = [
                    {"component": "SOLE-RBR",    "description": "Outsole",     "quantity": 2,   "uom": "pcs","order": 1},
                    {"component": "THR-40",      "description": "Thread",      "quantity": 1,   "uom": "pcs","order": 2},
                ]

            comp_map = {c.code: c for c in ProductTemplate.objects.filter(code__in=[ln["component"] for ln in lines])}
            for row in lines:
                BomLine.objects.create(
                    bom=bom,
                    component=comp_map[row["component"]],
                    description=row["description"],
                    quantity=row["quantity"],
                    uom=row["uom"],
                    order=row["order"],
                )

        # ---- A sample Change Request (v1.0 -> v1.1) ----
        for prod in products:
            v_from = versions[prod.code]
            v_to, _ = ProductVersion.objects.get_or_create(
                product=prod,
                version_code="v1.1",
                defaults=allow(
                    ProductVersion,
                    {
                        "title": f"{prod.name} revision",
                        "status": "approved",
                        "is_active": True,
                        "effective_from": now,
                    },
                ),
            )

            cr, _ = ChangeRequest.objects.get_or_create(
                number=f"ECO-{prod.code}-001",
                defaults=allow(
                    ChangeRequest,
                    {
                        "product": prod,
                        "from_version": v_from,
                        "to_version": v_to,
                        "change_type": "design",
                        "reason": "Demo: minor pattern adjustment",
                        "status": "implemented",
                        "requested_by": "plm_system",
                        "approved_by": "plm_manager",
                        "approved_at": timezone.now(),
                        "implemented_at": timezone.now(),
                    },
                ),
            )

            doc = PLMDocument.objects.filter(name=f"{prod.name} Tech Pack").first()
            if doc:
                cr.attachments.add(doc)

            bom = Bom.objects.filter(product_version=v_from).first()
            if bom:
                bom_line = bom.lines.order_by("order").first()
                ChangeRequestItem.objects.get_or_create(
                    change_request=cr,
                    bom=bom,
                    bom_line=bom_line,
                    defaults={"note": "Auto-linked demo item"},
                )

        self.stdout.write(self.style.SUCCESS("PLM seed completed successfully."))

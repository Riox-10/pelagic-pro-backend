from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from core.models import Product


PRODUCTS = [
    {
        "name": "Sardines à l’huile Végétale",
        "brand": "PALMA",
        "category": "Sardines",
        "filename": "palma-sardines-huile-vegetale.png",
        "weight": "125g",
        "packaging": "x 50",
        "description": "Sardines préparées à l’huile végétale, conditionnées dans un format pratique adapté à la distribution professionnelle.",
    },
    {
        "name": "Sardines à l’huile Végétale Pimentée",
        "brand": "PALMA",
        "category": "Sardines",
        "filename": "palma-sardines-huile-vegetale-pimentee.png",
        "weight": "125g",
        "packaging": "x 50",
        "description": "Version pimentée des sardines à l’huile végétale.",
    },
    {
        "name": "Sardines à la Sauce Tomate",
        "brand": "PALMA",
        "category": "Sardines",
        "filename": "palma-sardines-sauce-tomate.png",
        "weight": "125g",
        "packaging": "x 50",
        "description": "Sardines à la sauce tomate, une référence classique de conserve.",
    },
    {
        "name": "Sardines à l’huile de Tournesol",
        "brand": "PALMA",
        "category": "Sardines",
        "filename": "palma-sardines-huile-tournesol.png",
        "weight": "125g",
        "packaging": "x 50",
        "description": "Sardines préparées à l’huile de tournesol.",
    },
    {
        "name": "Morceaux de Maquereaux à l’huile Végétale",
        "brand": "PALMA",
        "category": "Maquereaux",
        "filename": "palma-maquereaux-huile-vegetale.png",
        "weight": "125g",
        "packaging": "x 50",
        "description": "Morceaux de maquereaux à l’huile végétale.",
    },
    {
        "name": "Filets de Maquereaux au Naturel Avec Citron",
        "brand": "PALMA",
        "category": "Maquereaux",
        "filename": "palma-filets-maquereaux-naturel-citron.png",
        "weight": "125g",
        "packaging": "x 50",
        "description": "Filets de maquereaux au naturel avec citron.",
    },
    {
        "name": "Filets de Maquereaux à l’huile de Tournesol",
        "brand": "PALMA",
        "category": "Maquereaux",
        "filename": "palma-filets-maquereaux-huile-tournesol.png",
        "weight": "125g",
        "packaging": "x 50",
        "description": "Filets de maquereaux à l’huile de tournesol.",
    },
]
PRODUCTS += [
    {
        "name": "Morceaux de Maquereaux à la Sauce Tomate 80g",
        "brand": "PALMA",
        "category": "Maquereaux",
        "filename": "palma-maquereaux-sauce-tomate-80g.png",
        "weight": "80g",
        "packaging": "x 25",
        "description": "Morceaux de maquereaux à la sauce tomate en petit format.",
    },
    {
        "name": "Morceaux de Maquereaux à la Sauce Tomate 425g",
        "brand": "PALMA",
        "category": "Maquereaux",
        "filename": "palma-maquereaux-sauce-tomate-425g.png",
        "weight": "425g",
        "packaging": "x 12",
        "description": "Morceaux de maquereaux à la sauce tomate en grand format.",
    },
    {
        "name": "Filets de Bonite à l’huile Végétale",
        "brand": "PALMA",
        "category": "Bonites",
        "filename": "palma-bonite-huile-vegetale.png",
        "weight": "1700g / 1,7kg",
        "packaging": "x 2",
        "description": "Filets de bonite à l’huile végétale en grand format.",
    },
    {
        "name": "Emiettés de Sardines à la Sauce Tomate Piquante",
        "brand": "Lyra",
        "category": "Sardines",
        "filename": "lyra-emiettes-sardines-sauce-tomate-piquante.png",
        "weight": "125g",
        "packaging": "x 50",
        "description": "Émiettés de sardines à la sauce tomate piquante.",
    },
    {
        "name": "Morcelets de Maquereaux à la Sauce Sevillana Piquante",
        "brand": "Lyra",
        "category": "Maquereaux",
        "filename": "lyra-maquereaux-sevillana-piquante.png",
        "weight": "125g",
        "packaging": "x 50",
        "description": "Morcelets de maquereaux à la sauce Sevillana piquante.",
    },
    {
        "name": "Morcelets de Maquereaux à la Sauce Tomate aux légumes et aux Épices",
        "brand": "Lyra",
        "category": "Maquereaux",
        "filename": "lyra-maquereaux-sauce-tomate-legumes-epices.png",
        "weight": "125g",
        "packaging": "x 50",
        "description": "Morcelets de maquereaux à la sauce tomate aux légumes et aux épices.",
    },
    {
        "name": "Filets de Maquereaux à l’huile Végétale",
        "brand": "Lyra",
        "category": "Maquereaux",
        "filename": "lyra-filets-maquereaux-huile-vegetale.png",
        "weight": "125g",
        "packaging": "x 50",
        "description": "Filets de maquereaux à l’huile végétale.",
    },
]


class Command(BaseCommand):
    help = "Import default products into the Django database."

    def handle(self, *args, **options):
        assets_dir = Path(settings.BASE_DIR) / "import_assets" / "products"

        if not assets_dir.exists():
            self.stderr.write(self.style.ERROR(f"Folder not found: {assets_dir}"))
            return

        for item in PRODUCTS:
            image_path = assets_dir / item["filename"]

            if not image_path.exists():
                self.stderr.write(self.style.WARNING(f"Image not found: {image_path}"))
                continue

            product = Product.objects.filter(
                name=item["name"],
                brand=item["brand"],
                weight=item["weight"],
            ).first()

            created = False

            if product is None:
                product = Product(
                    name=item["name"],
                    brand=item["brand"],
                    weight=item["weight"],
                )
                created = True

            product.category = item["category"]
            product.packaging = item["packaging"]
            product.description = item["description"]
            product.is_active = True

            with image_path.open("rb") as image_file:
                product.image.save(
                    item["filename"],
                    File(image_file),
                    save=False,
                )

            product.save()

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created: {item['name']}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Updated: {item['name']}"))

        self.stdout.write(self.style.SUCCESS("Products import completed successfully."))
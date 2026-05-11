from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from core.models import GalleryImage


GALLERY_ITEMS = [
    {
        "title": "Sardines",
        "filename": "sardines-assiette.png",
        "description": "Produit de la mer riche en protéines et apprécié pour sa valeur nutritionnelle.",
    },
    {
        "title": "Bonite",
        "filename": "bonite-assiette.png",
        "description": "Poisson utilisé dans plusieurs préparations, reconnu pour sa qualité et son goût.",
    },
    {
        "title": "Filets de maquereaux",
        "filename": "filets-maquereaux.png",
        "description": "Le maquereau est un poisson pélagique riche en nutriments essentiels.",
    },
    {
        "title": "Sardines à la sauce tomate",
        "filename": "sardines-sauce-tomate.webp",
        "description": "Une préparation savoureuse à base de sardines et de sauce tomate.",
    },
    {
        "title": "Sardines au citron",
        "filename": "sardines-citron-pain.webp",
        "description": "Une présentation équilibrée des sardines avec une touche de citron.",
    },
    {
        "title": "Sardines toast",
        "filename": "sardines-toast.webp",
        "description": "Les sardines peuvent être consommées dans des préparations pratiques et variées.",
    },
    {
        "title": "Sardines à l’huile",
        "filename": "sardines-boite-huile.webp",
        "description": "Conserve de sardines à l’huile, pratique et adaptée à plusieurs modes de consommation.",
    },
    {
        "title": "Sardines en conserve",
        "filename": "sardines-boite-table.webp",
        "description": "Produit conditionné permettant une bonne conservation et une utilisation facile.",
    },
    {
        "title": "Maquereaux",
        "filename": "maquereaux-boite.png",
        "description": "Le maquereau est apprécié pour sa richesse nutritionnelle et sa qualité gustative.",
    },
    {
        "title": "Thon et bonite",
        "filename": "thon-bonite-filet.png",
        "description": "Produits de la mer riches et adaptés à une alimentation variée.",
    },
]


class Command(BaseCommand):
    help = "Import default gallery images into the Django database."

    def handle(self, *args, **options):
        assets_dir = Path(settings.BASE_DIR) / "import_assets" / "gallery"

        if not assets_dir.exists():
            self.stderr.write(
                self.style.ERROR(f"Folder not found: {assets_dir}")
            )
            return

        for item in GALLERY_ITEMS:
            image_path = assets_dir / item["filename"]

            if not image_path.exists():
                self.stderr.write(
                    self.style.WARNING(f"Image not found: {image_path}")
                )
                continue

            gallery_image, created = GalleryImage.objects.get_or_create(
                title=item["title"],
                defaults={
                    "description": item["description"],
                    "is_active": True,
                },
            )

            gallery_image.description = item["description"]
            gallery_image.is_active = True

            with image_path.open("rb") as image_file:
                gallery_image.image.save(
                    item["filename"],
                    File(image_file),
                    save=False,
                )

            gallery_image.save()

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Created: {item['title']}")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"Updated: {item['title']}")
                )

        self.stdout.write(
            self.style.SUCCESS("Gallery import completed successfully.")
        )
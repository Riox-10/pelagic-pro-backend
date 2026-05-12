from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from core.models import CompanyImage


COMPANY_IMAGES = [
    {
        "title": "Ligne de production",
        "filename": "company-1-production-line.jpg",
        "alt": "Ligne de production Pelagic Pro",
        "order": 1,
    },
    {
        "title": "Salle de traitement",
        "filename": "company-2-processing-room.jpg",
        "alt": "Salle de traitement Pelagic Pro",
        "order": 2,
    },
    {
        "title": "Machines industrielles",
        "filename": "company-3-machinery.jpg",
        "alt": "Machines industrielles Pelagic Pro",
        "order": 3,
    },
    {
        "title": "Ligne d'emballage",
        "filename": "company-4-packaging-line.jpg",
        "alt": "Ligne d'emballage Pelagic Pro",
        "order": 4,
    },
]


class Command(BaseCommand):
    help = "Import default company presentation images into the Django database."

    def handle(self, *args, **options):
        assets_dir = Path(settings.BASE_DIR) / "import_assets" / "company"

        if not assets_dir.exists():
            self.stderr.write(self.style.ERROR(f"Folder not found: {assets_dir}"))
            return

        for item in COMPANY_IMAGES:
            image_path = assets_dir / item["filename"]

            if not image_path.exists():
                self.stderr.write(self.style.WARNING(f"Image not found: {image_path}"))
                continue

            company_image, created = CompanyImage.objects.get_or_create(
                title=item["title"],
                defaults={
                    "alt": item["alt"],
                    "order": item["order"],
                    "is_active": True,
                },
            )

            company_image.alt = item["alt"]
            company_image.order = item["order"]
            company_image.is_active = True

            with image_path.open("rb") as image_file:
                company_image.image.save(
                    item["filename"],
                    File(image_file),
                    save=False,
                )

            company_image.save()

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created: {item['title']}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Updated: {item['title']}"))

        self.stdout.write(
            self.style.SUCCESS("Company images import completed successfully.")
        )
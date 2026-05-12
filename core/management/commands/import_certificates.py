from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from core.models import Certificate


CERTIFICATES = [
    {
        "name": "U Certification",
        "filename": "certificat-1-u.png",
        "alt": "Certificat U Certification",
    },
    {
        "name": "BRCGS Food Safety",
        "filename": "certificat-2-brcgs-food-safety.png",
        "alt": "Certificat BRCGS Food Safety",
    },
    {
        "name": "ONSSA",
        "filename": "certificat-3-onssa.png",
        "alt": "Certificat ONSSA",
    },
    {
        "name": "FDA",
        "filename": "certificat-4-fda.png",
        "alt": "Certificat FDA",
    },
    {
        "name": "IFS Food",
        "filename": "certificat-5-ifs-food.png",
        "alt": "Certificat IFS Food",
    },
    {
        "name": "amfori",
        "filename": "certificat-6-amfori.png",
        "alt": "Certificat amfori",
    },
    {
        "name": "Friend of the Sea",
        "filename": "certificat-7-friend-of-the-sea.png",
        "alt": "Certificat Friend of the Sea",
    },
]


class Command(BaseCommand):
    help = "Import default certificates into the Django database."

    def handle(self, *args, **options):
        assets_dir = Path(settings.BASE_DIR) / "import_assets" / "certificates"

        if not assets_dir.exists():
            self.stderr.write(
                self.style.ERROR(f"Folder not found: {assets_dir}")
            )
            return

        for item in CERTIFICATES:
            image_path = assets_dir / item["filename"]

            if not image_path.exists():
                self.stderr.write(
                    self.style.WARNING(f"Image not found: {image_path}")
                )
                continue

            certificate, created = Certificate.objects.get_or_create(
                name=item["name"],
                defaults={
                    "alt": item["alt"],
                },
            )

            certificate.alt = item["alt"]

            with image_path.open("rb") as image_file:
                certificate.image.save(
                    item["filename"],
                    File(image_file),
                    save=False,
                )

            certificate.save()

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Created: {item['name']}")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"Updated: {item['name']}")
                )

        self.stdout.write(
            self.style.SUCCESS("Certificates import completed successfully.")
        )
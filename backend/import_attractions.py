
import csv
import os
import django
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from core.models import Attraction

CSV_FILE = Path(__file__).parent / "data.csv"

added = 0
skipped = 0

with open(CSV_FILE, "r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        name = row["Name"].strip()
        city = row["City"].strip()

        if not name or not city:
            skipped += 1
            continue

        # Avoid duplicate attractions
        exists = Attraction.objects.filter(
            name__iexact=name,
            location__iexact=city
        ).exists()

        if exists:
            skipped += 1
            continue

        details = [
            row.get("Type", ""),
            row.get("Significance", ""),
            f"Best time to visit: {row.get('Best Time to visit', '')}",
            f"Estimated visiting time: {row.get('time needed to visit in hrs', '')} hours",
            f"Google rating: {row.get('Google review rating', '')}",
            f"Entrance fee: ₹{row.get('Entrance Fee in INR', '')}",
        ]

        description = " | ".join(
            item for item in details
            if item and item.strip() and item.strip().lower() != "none"
        )

        Attraction.objects.create(
            name=name,
            location=city,
            description=description,
            opening_time=None,
            closing_time=None,
            latitude=None,
            longitude=None
        )

        added += 1

print("Import completed!")
print("New attractions added:", added)
print("Duplicates/invalid records skipped:", skipped)
print("Total attractions in database:", Attraction.objects.count())

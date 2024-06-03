from django.core.management.base import BaseCommand
import json
from ...models import Ayat, Ruku, HizbQuarter, Juz
import os


def seed_ayats():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_dir = os.path.join(current_dir, "..", "..", "bootstrap_data")
    json_file_name = "ayats_data.json"
    path_to_json = os.path.join(json_file_dir, json_file_name)

    with open(path_to_json, "r") as file:
        data = json.load(file)
        ayats = []
        for item in data["ayats"]:
            ayat = Ayat(**item)
            ayats.append(ayat)

        Ayat.objects.bulk_create(ayats)
        return "done"


def seed_rukus():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_dir = os.path.join(current_dir, "..", "..", "bootstrap_data")
    json_file_name = "rukus_data.json"
    path_to_json = os.path.join(json_file_dir, json_file_name)
    with open(path_to_json, "r") as file:
        data = json.load(file)

    # Loop over each item in the JSON data
    for item in data["rukus"]:
        # Create a Ruku instance for the current item
        ruku_instance = Ruku.objects.create(number=item["number"])

        # Fetch the Ayat instances based on their IDs provided in the JSON
        ayat_instances = Ayat.objects.filter(id__in=item["ayat"])

        # Use the set method to associate the Ayat instances with the Ruku instance
        ruku_instance.ayat.set(ayat_instances)

    return "Rukus and associated Ayats seeded successfully."


def seed_hizb_quarters():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_dir = os.path.join(current_dir, "..", "..", "bootstrap_data")
    json_file_name = "hizb_quarters_data.json"
    path_to_json = os.path.join(json_file_dir, json_file_name)
    with open(path_to_json, "r") as file:
        data = json.load(file)

    for item in data["hizbQuarters"]:
        juz = Juz.objects.get(number=item["juz"])
        # Create a HizbQuarter instance for the current item
        hizb_quarter_instance = HizbQuarter.objects.create(
            juz=juz, number=item["number"]
        )

        # Fetch the Ayat instances based on their IDs provided in the JSON
        # This assumes that the ayat IDs are sequential and match the numbers provided.
        # If your Ayat model's IDs don't match, you'll need to adjust this query accordingly.
        ayat_instances = Ayat.objects.filter(id__in=item["ayat"])

        # Use the set method to associate the Ayat instances with the HizbQuarter instance
        hizb_quarter_instance.ayat.set(ayat_instances)

    return "HizbQuarters and associated Ayats seeded successfully."


def seed_juzs():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_dir = os.path.join(current_dir, "..", "..", "bootstrap_data")
    json_file_name = "juz_data.json"
    path_to_json = os.path.join(json_file_dir, json_file_name)
    with open(path_to_json, "r") as file:
        data = json.load(file)

    # Loop over each item in the JSON data
    for item in data["juz"]:
        # Create a Juz instance for the current item
        juz_instance = Juz.objects.create(number=item["number"])

        # Fetch the Ayat instances based on their IDs provided in the JSON
        ayat_instances = Ayat.objects.filter(id__in=item["ayat"])

        # Use the set method to associate the Ayat instances with the Juz instance
        juz_instance.ayat.set(ayat_instances)

    return "Juz and associated Ayats seeded successfully."


class Command(BaseCommand):
    help = "Seeds the database with data from JSON files"

    def handle(self, *args, **options):

        seed_ayats()
        seed_rukus()
        seed_juzs()
        seed_hizb_quarters()
        self.stdout.write(self.style.SUCCESS("Data seeding complete"))

        return "done"

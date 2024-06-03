import datetime
import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from ayats.models import Ayat, UserAyatState


class Command(BaseCommand):
    help = "Seeds the database with UserState data"

    def handle(self, *args, **options):

        user = get_user_model().objects.all().first()

        juz_ayat_dict = {
            1: [1, 148],
            2: [149, 259],
            3: [260, 385],
            4: [386, 516],
            5: [517, 640],
            6: [641, 750],
            7: [751, 899],
            8: [900, 1041],
            9: [1042, 1200],
            10: [1201, 1328],
            11: [1329, 1478],
            12: [1479, 1648],
            13: [1649, 1802],
            14: [1803, 2029],
            15: [2030, 2214],
            16: [2215, 2483],
            17: [2484, 2673],
            18: [2674, 2875],
            19: [2876, 3214],
            20: [3215, 3385],
            21: [3386, 3563],
            22: [3564, 3732],
            23: [3733, 4089],
            24: [4090, 4264],
            25: [4265, 4510],
            26: [4511, 4705],
            27: [4706, 5104],
            28: [5105, 5241],
            29: [5242, 5672],
            30: [5673, 6236],
        }

        for juz in range(1, 31):
            range_start, range_end = juz_ayat_dict[juz]
            default_expiry_time = user.default_expiry_time
            random_days = random.randint(1, default_expiry_time)
            expiration_date = timezone.now() + timedelta(days=random_days)

            # Choose a random start and end within the range
            start_number = random.randint(range_start, range_end)
            end_number = random.randint(
                start_number, range_end
            )  # Ensure that end is after the start

            # Fetch sequential ayat from the calculated range
            ayats = Ayat.objects.filter(number__range=(start_number, end_number))

            # You can do something with the fetched Ayats here
            # For example, print them or store them for further processing
            print(f"Juz {juz}: Selected Ayats from {start_number} to {end_number}.")

            user_state_ayats = UserAyatState.objects.create(
                user=user, expiration_date=expiration_date
            )
            user_state_ayats.ayat.set(ayats)
            user_state_ayats.save()

        self.stdout.write(self.style.SUCCESS("Added User States Successfully"))

        return "done"

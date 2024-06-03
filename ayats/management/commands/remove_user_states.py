from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from ayats.models import UserAyatState


class Command(BaseCommand):
    help = "Seeds the database with UserState data"

    def handle(self, *args, **options):

        user = get_user_model().objects.all().first()
        user_states = UserAyatState.objects.filter(user=user)
        user_states.delete()

        self.stdout.write(self.style.SUCCESS("Removed All User States Successfully"))

        return "done"

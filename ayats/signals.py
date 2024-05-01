from django.db import transaction
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import UserAyatState
from .tasks import update_user_states

import logging

LOGGER = logging.getLogger(__name__)


@receiver(m2m_changed, sender=UserAyatState.ayat.through)
def update_user_ayat_state(sender, instance, action, **kwargs):
    logging.info("update_user_ayat_state signal fired")

    if action == "post_add":

        with transaction.atomic():

            instance.update_overlapping_user_states()

            transaction.on_commit(lambda: update_user_states(instance.id))

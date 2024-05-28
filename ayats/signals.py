from django.db import transaction
from django.db.models.signals import m2m_changed, pre_delete, pre_save
from django.dispatch import receiver
from .models import UserAyatState
from .tasks import update_hizb_and_juz_states, cleanup_user_states

import logging

logger = logging.getLogger("custom_logger")


# The many-to-many signal is used to update the UserAyatState objects
# when the ayat relationship is altered. Notice the "action" parameter
# which tells us what action was taken on the relationship.
@receiver(m2m_changed, sender=UserAyatState.ayat.through)
def update_user_ayat_state(sender, instance, action, **kwargs):
    # if action == "post_add" or action == "post_remove" or action == "post_clear":
    if action in ["post_add"]:
        logger.info("SIGNAL: AYAT ALTERED ON USER STATE")
        logger.info(f"action: {action}")

        with transaction.atomic():
            instance.update_overlapping_user_states()

            user = instance.user
            ayats = instance.ayat.all()

            # transaction.on_commit makes sure the task is run after the current transaction is committed
            # i.e. after the UserAyatState object and its ayat relationship is saved
            transaction.on_commit(lambda: update_hizb_and_juz_states(user.id, ayats))


# Using the pre_save signal with a transaction.on_commit to ensure
# that the task is run after the current transaction is committed.
@receiver(pre_save, sender=UserAyatState)
def update_user_ayat_state_on_save(sender, instance, **kwargs):
    logger.info("SIGNAL: USER STATE PRE SAVE")

    if instance.pk:
        with transaction.atomic():
            user = instance.user
            ayats = instance.ayat.all()
            transaction.on_commit(lambda: update_hizb_and_juz_states(user.id, ayats))


# Pre Delete signal to update the UserAyatState objects when an object is deleted
# And only cleanup the UserHizb and UserJuzState objects after the transaction is committed
@receiver(pre_delete, sender=UserAyatState)
def update_user_ayat_state_on_delete(sender, instance, **kwargs):
    logger.info("SIGNAL: USER STATE PRE DELETE")

    user = instance.user
    ayats = list(instance.ayat.all())  # Force evaluation of the queryset
    # Once we grab the ayats, I can clear the ayat relationship
    instance.ayat.clear()  # This will Set the weight to 0
    update_hizb_and_juz_states(user.id, ayats)

    # Cleanup the UserHizb and UserJuz states after the transaction is committed
    with transaction.atomic():
        transaction.on_commit(lambda: cleanup_user_states())

from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import UserAyatState


@receiver(m2m_changed, sender=UserAyatState.ayat.through)
def update_user_ayat_state(sender, instance, action, **kwargs):
    if action == "post_add":
        instance.update_overlapping_user_states()

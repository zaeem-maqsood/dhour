from django.contrib.auth import get_user_model

from .models import (
    UserAyatState,
    UserHizbState,
    HizbQuarter,
    UserJuzState,
    Juz,
    calculate_hizb_weight,
    calculate_juz_weight,
)

import logging

LOGGER = logging.getLogger(__name__)


def update_user_states(user_ayat_state_id):
    """
    Update the UserHizbState and UserJuzState objects based on the UserAyatState object with the given ID.
    """

    logging.info(
        f"update_user_states task fired for UserAyatState with id {user_ayat_state_id}"
    )

    # Retrieve the UserAyatState object based on the given ID
    try:
        user_ayat_state = UserAyatState.objects.get(pk=user_ayat_state_id)
    except UserAyatState.DoesNotExist:
        raise ValueError(f"UserAyatState with id {user_ayat_state_id} does not exist.")

    user = user_ayat_state.user
    ayats = user_ayat_state.ayat.all()

    # Pre-fetch the related HizbQuarters and Juz based on the ayats
    hizb_quarters = HizbQuarter.objects.filter(ayat__in=ayats)
    juz_list = Juz.objects.filter(ayat__in=ayats)

    # Update UserHizbState without looping over ayats
    hizb_states = []
    for hizb_quarter in hizb_quarters:
        user_hizb_state, _ = UserHizbState.objects.get_or_create(
            user=user, hizb=hizb_quarter
        )
        user_hizb_state.weight = calculate_hizb_weight(user, hizb_quarter)
        user_hizb_state.save()
        hizb_states.append(user_hizb_state)

    # Update UserJuzState without looping over ayats
    juz_states = []
    for juz in juz_list:
        user_juz_state, _ = UserJuzState.objects.get_or_create(user=user, juz=juz)
        user_juz_state.weight = calculate_juz_weight(user, juz)
        user_juz_state.save()
        juz_states.append(user_juz_state)

    return {"hizb_states": hizb_states, "juz_states": juz_states}

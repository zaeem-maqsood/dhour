import logging
from .models import (
    UserAyatState,
    UserHizbState,
    HizbQuarter,
    UserJuzState,
    Juz,
    Ayat,
    calculate_hizb_weight,
    calculate_juz_weight,
)
from users.models import User


logger = logging.getLogger("custom_logger")


def update_hizb_and_juz_states(user_id, ayats):

    user = User.objects.get(pk=user_id)
    # Pre-fetch the related HizbQuarters and Juz based on the ayats
    hizb_quarters_query = HizbQuarter.objects.filter(ayat__in=ayats).distinct()
    hizb_quarters = list(hizb_quarters_query)  # Force evaluation of the queryset
    juz_query = Juz.objects.filter(ayat__in=ayats).distinct()
    juz_list = list(juz_query)  # Force evaluation of the queryset

    print(hizb_quarters)
    # Update UserHizbStates
    hizb_states = []
    for hizb_quarter in hizb_quarters:
        user_hizb_state, _ = UserHizbState.objects.get_or_create(
            user=user, hizb=hizb_quarter
        )
        print(user_hizb_state)
        user_hizb_state.weight = calculate_hizb_weight(user, hizb_quarter)
        user_hizb_state.save()
        hizb_states.append(user_hizb_state)

    # Update UserJuzState
    juz_states = []
    for juz in juz_list:
        user_juz_state, _ = UserJuzState.objects.get_or_create(user=user, juz=juz)
        user_juz_state.weight = calculate_juz_weight(user, juz)
        user_juz_state.save()
        juz_states.append(user_juz_state)

    return {"hizb_states": hizb_states, "juz_states": juz_states}


def cleanup_user_states():
    """
    Clean up UserHizbState and UserJuzState objects potentially orphaned after a UserAyatState deletion.
    This function checks for any HizbQuarter or Juz that no longer have associated Ayat linked through any UserAyatState,
    and deletes or updates the corresponding state objects accordingly.
    """
    logger.info("----- Cleanup User States ------")

    user_ayat_states = UserAyatState.objects.filter(weight=0)
    user_ayat_states.delete()

    user_hizb_states = UserHizbState.objects.filter(weight=0)
    user_hizb_states.delete()

    user_juz_states = UserJuzState.objects.filter(weight=0)
    user_juz_states.delete()

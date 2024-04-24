import datetime
import pytest
import pytz

from django.utils import timezone

from ayats.models import Ayat, HizbQuarter, Juz, Ruku, UserAyatState, UserHizbState
from users.models import User

# Create your tests here.
import logging

LOGGER = logging.getLogger(__name__)


def test_make_sure_records_exist(bootstrap_data):

    LOGGER.info("Sanity check to make sure the data is loaded correctly")
    assert Ayat.objects.count() == 6236
    assert HizbQuarter.objects.count() == 240
    assert Juz.objects.count() == 30
    assert Ruku.objects.count() == 556


# Test to make sure the user states are created correctly
# and if another user state is created with overlapping ayats
# the overlapping user states are updated correctly
def test_user_states_override(bootstrap_data):
    logging.info("Get the first 7 ayat of Surah Fatiha")
    surah = 1
    ayat_start = 1
    ayat_end = 7
    ayats = Ayat.objects.filter(
        surah=surah, ayat_in_surah__range=(ayat_start, ayat_end)
    )
    assert ayats.count() == 7

    logging.info(
        "Create a user and assign the first 7 ayat of Surah Fatiha to the user"
    )
    expiration_date = timezone.now() + datetime.timedelta(days=16)
    user = User.objects.get(username="iman")
    user_state_ayats = UserAyatState.objects.create(
        user=user, expiration_date=expiration_date
    )
    user_state_ayats.ayat.set(ayats)
    user_state_ayats.save()
    assert user_state_ayats.ayat.count() == 7

    logging.info("Create a new user state with the first 3 ayat of Surah Fatiha")
    user_state_ayats_2 = UserAyatState.objects.create(
        user=user, expiration_date=expiration_date
    )
    user_state_ayats_2.ayat.set(ayats[:3])
    user_state_ayats_2.save()

    logging.info("Check if the overlapping user states are updated correctly")
    assert user_state_ayats.ayat.count() == 4
    assert user_state_ayats_2.ayat.count() == 3

    logging.info("Create a new user state that overlaps both the previous user states")
    user_state_ayats_3 = UserAyatState.objects.create(
        user=user, expiration_date=expiration_date
    )
    user_state_ayats_3.ayat.set(ayats)
    user_state_ayats_3.save()

    logging.info("Check if the user states were deleted correctly")
    assert UserAyatState.objects.count() == 1


def test_user_ayat_state_weight(bootstrap_data):
    logging.info("Make sure the weight is calculated correctly")

    user = User.objects.get(username="iman")
    default_expiry_time = user.default_expiry_time
    logging.info(f"Default expiry time for user {user} is {default_expiry_time}")
    assert default_expiry_time == 30

    expiration_date = timezone.now() + datetime.timedelta(days=16)
    surah = 1
    ayat_start = 1
    ayat_end = 7
    ayats = Ayat.objects.filter(
        surah=surah, ayat_in_surah__range=(ayat_start, ayat_end)
    )

    user_state = UserAyatState.objects.create(
        user=user, expiration_date=expiration_date
    )
    user_state.ayat.set(ayats)
    user_state.save()

    logging.info(f"User state weight for user {user} is {user_state.weight}")
    # Not reliable to test floating point numbers for equality
    assert user_state.weight == pytest.approx(0.5, rel=1e-9)

    # Create more user states to test the weight calculation
    surah = 2
    ayat_start = 1
    ayat_end = 30
    ayats = Ayat.objects.filter(
        surah=surah, ayat_in_surah__range=(ayat_start, ayat_end)
    )
    user_state_2 = UserAyatState.objects.create(
        user=user, expiration_date=expiration_date
    )
    user_state_2.ayat.set(ayats)
    user_state_2.save()
    logging.info(f"User state weight for user {user} is {user_state_2.weight}")

    assert UserAyatState.objects.count() == 2

    surah = 2
    ayat_start = 25
    ayat_end = 50
    ayats = Ayat.objects.filter(
        surah=surah, ayat_in_surah__range=(ayat_start, ayat_end)
    )
    user_state_3 = UserAyatState.objects.create(
        user=user, expiration_date=expiration_date
    )
    user_state_3.ayat.set(ayats)
    user_state_3.save()
    logging.info(f"User state weight for user {user} is {user_state_3.weight}")

    # Make a user ayat state that is not in the hizb quarter
    surah = 2
    ayat_start = 50
    ayat_end = 60
    ayats = Ayat.objects.filter(
        surah=surah, ayat_in_surah__range=(ayat_start, ayat_end)
    )
    user_state_4 = UserAyatState.objects.create(
        user=user, expiration_date=expiration_date
    )
    user_state_4.ayat.set(ayats)
    user_state_4.save()

    assert UserAyatState.objects.count() == 4

    from .tasks import update_hizb_weight_task

    hizb_quarter = HizbQuarter.objects.get(id=1)
    logging.info(f"Updating the weight for user {user} for hizb quarter {hizb_quarter}")
    user_hizb_state, created = UserHizbState.objects.get_or_create(
        user=user, hizb=hizb_quarter
    )
    assert user_hizb_state.weight == 0

    update_hizb_weight_task(user.id, hizb_quarter.id)
    user_hizb_state.refresh_from_db()

    assert user_hizb_state.weight == pytest.approx(0.5, rel=1e-9)

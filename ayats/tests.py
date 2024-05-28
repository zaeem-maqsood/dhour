import datetime
import pytest
import pytz

from django.utils import timezone
from users.models import User
from ayats.models import (
    Ayat,
    HizbQuarter,
    Juz,
    Ruku,
    UserAyatState,
    UserHizbState,
    UserJuzState,
)
from unittest.mock import MagicMock
from django.db.models.signals import m2m_changed
from django.db import transaction

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

    # Create user
    user = User.objects.create(
        email="zaeem.maqsood@gmail.com",
        is_active=True,
        is_staff=True,
        is_superuser=True,
    )

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
    user = User.objects.get(email="zaeem.maqsood@gmail.com")
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


@pytest.mark.django_db(transaction=True)
def test_user_ayat_hizb_and_juz_states(bootstrap_data, mocker):
    logging.info("Testing User Ayat, Hizb, and Juz states")

    # Create user
    user = User.objects.create(
        email="zaeem.maqsood@gmail.com",
        is_active=True,
        is_staff=True,
        is_superuser=True,
    )

    user = User.objects.get(email="zaeem.maqsood@gmail.com")
    default_expiry_time = user.default_expiry_time
    logging.info(f"Default expiry time for user {user} is {default_expiry_time}")
    assert default_expiry_time == 30

    # Connect a mock handler to the m2m_changed signal
    mock_handler = mocker.MagicMock()
    m2m_changed.connect(mock_handler, sender=UserAyatState.ayat.through)

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
    with transaction.atomic():
        user_state.ayat.set(ayats)

    assert mock_handler.call_count == 2
    m2m_changed.disconnect(mock_handler, sender=UserAyatState.ayat.through)

    logging.info(f"User Ayat weight for user {user} is {user_state.weight}")
    # Not reliable to test floating point numbers for equality
    assert user_state.weight == pytest.approx(0.5, rel=1e-9)
    assert UserAyatState.objects.count() == 1

    user_hizb_state = UserHizbState.objects.get(user=user)
    user_hizb_state_weight = user_hizb_state.weight
    logging.info(f"User Hizb weight for user {user} is {user_hizb_state_weight}")
    assert UserHizbState.objects.count() == 1
    assert user_hizb_state_weight == pytest.approx(0.5, rel=1e-9)

    user_juz_state = UserJuzState.objects.get(user=user)
    user_juz_state_weight = user_juz_state.weight
    logging.info(f"User Juz weight for user {user} is {user_juz_state_weight}")
    assert UserJuzState.objects.count() == 1
    assert user_juz_state_weight == pytest.approx(0.5, rel=1e-9)

    # Connect a mock handler to the m2m_changed signal
    m2m_changed.connect(mock_handler, sender=UserAyatState.ayat.through)

    surah = 2
    ayat_start = 1
    ayat_end = 30
    ayats = Ayat.objects.filter(
        surah=surah, ayat_in_surah__range=(ayat_start, ayat_end)
    )
    user_state_2 = UserAyatState.objects.create(
        user=user, expiration_date=expiration_date
    )

    with transaction.atomic():
        user_state_2.ayat.set(ayats)

    m2m_changed.disconnect(mock_handler, sender=UserAyatState.ayat.through)

    assert mock_handler.call_count == 4

    assert UserAyatState.objects.count() == 2
    assert UserHizbState.objects.count() == 2
    assert UserJuzState.objects.count() == 1

    # Connect a mock handler to the m2m_changed signal
    m2m_changed.connect(mock_handler, sender=UserAyatState.ayat.through)

    surah = 2
    ayat_start = 25
    ayat_end = 124
    ayats = Ayat.objects.filter(
        surah=surah, ayat_in_surah__range=(ayat_start, ayat_end)
    )
    user_state_3 = UserAyatState.objects.create(
        user=user, expiration_date=expiration_date
    )

    with transaction.atomic():
        user_state_3.ayat.set(ayats)

    m2m_changed.disconnect(mock_handler, sender=UserAyatState.ayat.through)

    assert mock_handler.call_count == 8
    assert UserAyatState.objects.count() == 3
    assert UserHizbState.objects.count() == 8
    assert UserJuzState.objects.count() == 1

    # Connect a mock handler to the m2m_changed signal
    m2m_changed.connect(mock_handler, sender=UserAyatState.ayat.through)

    # Make a user ayat state that is not in the hizb quarter
    surah = 2
    ayat_start = 142
    ayat_end = 157
    ayats = Ayat.objects.filter(
        surah=surah, ayat_in_surah__range=(ayat_start, ayat_end)
    )
    user_state_4 = UserAyatState.objects.create(
        user=user, expiration_date=expiration_date
    )
    with transaction.atomic():
        user_state_4.ayat.set(ayats)

    m2m_changed.disconnect(mock_handler, sender=UserAyatState.ayat.through)

    logging.info("We should have 20 calls to the signal handler")
    assert mock_handler.call_count == 10
    user_ayat_states = UserAyatState.objects.all()
    for user_ayat_state in user_ayat_states:
        logging.info(
            f"User Ayat State {user_ayat_state} has weight {user_ayat_state.weight}"
        )
    logging.info(f"User Ayat State count: {user_ayat_states.count()}")
    assert user_ayat_states.count() == 4

    user_hizb_states = UserHizbState.objects.all()
    for user_hizb_state in user_hizb_states:
        logging.info(
            f"User Hizb State {user_hizb_state} has weight {user_hizb_state.weight}"
        )
    logging.info(f"User Hizb State count: {user_hizb_states.count()}")
    assert user_hizb_states.count() == 9

    user_juz_states = UserJuzState.objects.all()
    for user_juz_state in user_juz_states:
        logging.info(
            f"User Juz State {user_juz_state} has weight {user_juz_state.weight}"
        )
    logging.info(f"User Juz State count: {user_juz_states.count()}")
    assert user_juz_states.count() == 2

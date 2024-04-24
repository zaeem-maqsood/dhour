import pytest
from ayats.models import Ayat
from django.core.management import call_command


@pytest.fixture()
def bootstrap_data(db):
    call_command("bootstrap_data")
    return db

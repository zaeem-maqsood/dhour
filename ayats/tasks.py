from django.contrib.auth import get_user_model

from .models import UserHizbState, HizbQuarter
from .models import calculate_hizb_weight


def update_hizb_weight_task(user_id, hizb_quarter_id):
    user = get_user_model().objects.get(id=user_id)
    hizb_quarter = HizbQuarter.objects.get(id=hizb_quarter_id)

    total_weight = calculate_hizb_weight(user, hizb_quarter)

    user_hizb_state = UserHizbState.objects.get(user=user, hizb=hizb_quarter)
    user_hizb_state.weight = total_weight
    user_hizb_state.save()

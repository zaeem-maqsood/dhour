from rest_framework import serializers
from .models import (
    UserAyatState,
    UserHizbState,
    UserJuzState,
)


class UserAyatStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAyatState
        fields = "__all__"


class UserHizbStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserHizbState
        fields = "__all__"


class UserJuzStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserJuzState
        fields = "__all__"

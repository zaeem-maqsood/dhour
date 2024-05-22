from rest_framework import serializers
from .models import (
    Ayat,
    UserAyatState,
    UserHizbState,
    UserJuzState,
)


class AyatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ayat
        fields = "__all__"


class UserAyatStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAyatState
        exclude = ["user"]
        depth = 1


class UserHizbStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserHizbState
        fields = "__all__"


class UserJuzStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserJuzState
        fields = "__all__"

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


class UserJuzStateSerializer(serializers.Serializer):
    juz_number = serializers.IntegerField()
    weight = serializers.SerializerMethodField()

    def get_weight(self, obj):
        weight = obj["weight"]
        if weight != "n/a":
            weight = round(float(weight), 2)
        return weight

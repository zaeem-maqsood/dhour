from django.shortcuts import render
from .models import UserAyatState, UserHizbState, UserJuzState
from .serializers import (
    UserAyatStateSerializer,
    UserHizbStateSerializer,
    UserJuzStateSerializer,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


# Create your views here.
class UserAyatStateList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_ayat_states = UserAyatState.objects.filter(user=user)
        serializer = UserAyatStateSerializer(user_ayat_states, many=True)
        return Response(serializer.data)

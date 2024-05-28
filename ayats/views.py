from .models import UserAyatState, UserJuzState, Juz
from .serializers import (
    UserAyatStateSerializer,
    UserJuzStateSerializer,
)
from users.models import User
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


class JuzStateList(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        user = User.objects.all().first()
        all_juz = Juz.objects.all()
        user_juz_states = UserJuzState.objects.filter(user=user)

        # Create a dictionary of user juz states for quick lookups
        user_juz_dict = {state.juz.number: state for state in user_juz_states}
        response_data = []
        for juz in all_juz:
            if juz.number in user_juz_dict:
                weight = user_juz_dict[juz.number].weight
            else:
                weight = "n/a"
            response_data.append({"juz_number": juz.number, "weight": weight})

        serializer = UserJuzStateSerializer(response_data, many=True)
        return Response(serializer.data)

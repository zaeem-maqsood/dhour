from django.urls import path
from .views import UserAyatStateList, JuzStateList
from rest_framework.urlpatterns import format_suffix_patterns

urlpatters = [
    path("ayats/states/", UserAyatStateList.as_view()),
    path("juz/states/", JuzStateList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatters)

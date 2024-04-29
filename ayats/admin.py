from django.contrib import admin
from .models import (
    Ayat,
    UserAyatState,
    Ruku,
    HizbQuarter,
    Juz,
    UserHizbState,
    UserJuzState,
)

# Register your models here.
admin.site.register(Ayat)
admin.site.register(UserAyatState)
admin.site.register(Ruku)
admin.site.register(HizbQuarter)
admin.site.register(Juz)
admin.site.register(UserHizbState)
admin.site.register(UserJuzState)

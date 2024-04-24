from django.contrib import admin
from .models import Ayat, UserAyatState, Ruku, HizbQuarter, Juz

# Register your models here.
admin.site.register(Ayat)
admin.site.register(UserAyatState)
admin.site.register(Ruku)
admin.site.register(HizbQuarter)
admin.site.register(Juz)

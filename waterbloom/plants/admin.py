from django.contrib import admin
from .models import Plant, WateringLog, Favorite

admin.site.register(Plant)
admin.site.register(WateringLog)
admin.site.register(Favorite)
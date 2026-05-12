from django.contrib import admin
from .models import Plant, WateringLog, Favorite

@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ('name', 'plant_type', 'watering_frequency', 'last_watered')
    list_filter = ('plant_type',)
    search_fields = ('name',)

@admin.register(WateringLog)
class WateringLogAdmin(admin.ModelAdmin):
    list_display = ('plant', 'user', 'watered_at')
    list_filter = ('watered_at',)

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'plant')
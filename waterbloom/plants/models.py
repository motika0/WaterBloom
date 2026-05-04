from django.db import models
from django.contrib.auth.models import User

class PlantType(models.TextChoices):
    LEAFY = 'leafy', 'Декоративно-лиственное'
    FLOWERING = 'flowering', 'Цветущее'
    SUCCULENT = 'succulent', 'Суккулент'
    AMPEL = 'ampel', 'Ампельное/лиана'


class Plant(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название растения")
    watering_frequency = models.IntegerField(verbose_name="Частота полива (дней)")
    last_watered = models.DateField(null=True, blank=True, verbose_name="Дата последнего полива")
    plant_type = models.CharField(
        max_length=20, 
        choices=PlantType.choices, 
        default=PlantType.LEAFY,
        verbose_name="Тип растения"
    )
    
    def __str__(self):
        return self.name


class WateringLog(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, verbose_name="Растение")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name="Кто полил")
    watered_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время полива")
    
    def __str__(self):
        return f"{self.plant.name} — {self.watered_at.strftime('%d.%m.%Y')}"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, verbose_name="Растение")
    
    class Meta:
        unique_together = ('user', 'plant')
    
    def __str__(self):
        return f"{self.user.username} избранное {self.plant.name}"
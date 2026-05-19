from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta
from django.utils import timezone

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
    image = models.ImageField(upload_to='plants/', null=True, blank=True, verbose_name="Фото растения")
    
    def get_next_watering_date(self):
        if self.last_watered:
            return self.last_watered + timedelta(days=self.watering_frequency)
        return None
    
    def get_watering_dates(self, days=90):
        dates = []
        if self.last_watered:
            current = self.last_watered
            next_date = current + timedelta(days=self.watering_frequency)
            while next_date <= date.today() + timedelta(days=days):
                dates.append(next_date)
                next_date = next_date + timedelta(days=self.watering_frequency)
        return dates
    
    def needs_watering(self):
        next_date = self.get_next_watering_date()
        if next_date:
            return next_date <= date.today()
        return False
    
    def days_until_watering(self):
        next_date = self.get_next_watering_date()
        if next_date:
            return (next_date - date.today()).days
        return None
    
    def __str__(self):
        return self.name

class WateringLog(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, verbose_name="Растение")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Кто полил")
    watered_at = models.DateField(null=True, blank=True, verbose_name="Дата полива")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания записи")

    def __str__(self):
        if self.watered_at:
            return f"{self.plant.name} - {self.watered_at.strftime('%d.%m.%Y')}"
        return f"{self.plant.name} - дата не указана"

    class Meta:
        ordering = ['-watered_at']

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, verbose_name="Растение")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата добавления")

    class Meta:
        unique_together = ('user', 'plant')

    def __str__(self):
        return f"{self.user.username} - {self.plant.name}"
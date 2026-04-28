from django.db import models


class Plant(models.Model):
    name = models.CharField(max_length=100)
    watering_frequency = models.IntegerField()
    last_watered = models.DateField(null=True)

    def __str__(self):
        return self.name


class WateringLog(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    watered_at = models.DateTimeField(auto_now_add=True)


class Favorite(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
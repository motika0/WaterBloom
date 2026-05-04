from django import forms
from .models import Plant

class PlantForm(forms.ModelForm):
    class Meta:
        model = Plant
        fields = ['name', 'watering_frequency', 'plant_type', 'last_watered']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Например, Кактус'}),
            'watering_frequency': forms.NumberInput(attrs={'placeholder': 'Через сколько дней поливать'}),
            'last_watered': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'name': 'Название растения',
            'watering_frequency': 'Частота полива (дней)',
            'plant_type': 'Тип растения',
            'last_watered': 'Дата последнего полива',
        }
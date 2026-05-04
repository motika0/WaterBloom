from django.shortcuts import render
from .models import Plant, WateringLog, Favorite

def home(request):
    return render(request, 'plants/home.html')

def plant_list(request):
    plants = Plant.objects.all()
    return render(request, 'plants/plant_list.html', {'plants': plants})

def plant_detail(request, pk):
    plant = Plant.objects.get(id=pk)
    return render(request, 'plants/plant_detail.html', {'plant': plant})

def plant_add(request):
    if request.method == 'POST':
        from datetime import date
        plant = Plant.objects.create(
            name=request.POST['name'],
            watering_frequency=int(request.POST['watering_frequency']),
            plant_type=request.POST['plant_type'],
            last_watered=request.POST.get('last_watered') or date.today()
        )
        return render(request, 'plants/plant_detail.html', {'plant': plant})
    return render(request, 'plants/plant_form.html', {'plant': None})

def plant_edit(request, pk):
    plant = Plant.objects.get(id=pk)
    if request.method == 'POST':
        plant.name = request.POST['name']
        plant.watering_frequency = int(request.POST['watering_frequency'])
        plant.plant_type = request.POST['plant_type']
        if request.POST.get('last_watered'):
            plant.last_watered = request.POST['last_watered']
        plant.save()
        return render(request, 'plants/plant_detail.html', {'plant': plant})
    return render(request, 'plants/plant_form.html', {'plant': plant})

def plant_delete(request, pk):
    plant = Plant.objects.get(id=pk)
    plant.delete()
    plants = Plant.objects.all()
    return render(request, 'plants/plant_list.html', {'plants': plants})

def profile(request):
    favorites = Favorite.objects.all()
    watering_logs = WateringLog.objects.all().order_by('-watered_at')[:10]
    return render(request, 'plants/profile.html', {
        'favorites': favorites,
        'watering_logs': watering_logs
    })
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from datetime import date, timedelta
from calendar import monthrange
import json
from .models import Plant, WateringLog, Favorite

def home(request):
    return render(request, 'plants/home.html')

def plant_list(request):
    plants = Plant.objects.all()

    search = request.GET.get('search')
    if search:
        plants = plants.filter(name__icontains=search)

    plant_type = request.GET.get('type')
    if plant_type:
        plants = plants.filter(plant_type=plant_type)

    sort = request.GET.get('sort')
    if sort == 'name':
        plants = plants.order_by('name')
    elif sort == 'watering':
        plants = plants.order_by('watering_frequency')

    favorites = []
    if request.user.is_authenticated:
        favorites = Favorite.objects.filter(user=request.user).values_list('plant_id', flat=True)

    return render(request, 'plants/plant_list.html', {
        'plants': plants,
        'favorites': favorites
    })

def plant_detail(request, pk):
    plant = get_object_or_404(Plant, id=pk)
    
    favorites = []
    if request.user.is_authenticated:
        favorites = Favorite.objects.filter(user=request.user).values_list('plant_id', flat=True)
    
    return render(request, 'plants/plant_detail.html', {
        'plant': plant,
        'favorites': favorites
    })

def plant_add(request):
    if request.method == 'POST':
        plant = Plant.objects.create(
            name=request.POST['name'],
            watering_frequency=int(request.POST['watering_frequency']),
            plant_type=request.POST['plant_type']
        )

        if request.FILES.get('image'):
            plant.image = request.FILES['image']
            plant.save()

        return redirect('plant_detail', pk=plant.pk)

    return render(request, 'plants/plant_form.html', {'plant': None})

def plant_edit(request, pk):
    plant = get_object_or_404(Plant, id=pk)

    if request.method == 'POST':
        plant.name = request.POST['name']
        plant.watering_frequency = int(request.POST['watering_frequency'])
        plant.plant_type = request.POST['plant_type']

        if request.FILES.get('image'):
            plant.image = request.FILES['image']

        plant.save()
        return redirect('plant_detail', pk=plant.pk)

    return render(request, 'plants/plant_form.html', {'plant': plant})

def plant_delete(request, pk):
    plant = get_object_or_404(Plant, id=pk)

    if request.method == 'POST':
        plant.delete()
        return redirect('plant_list')

    return render(request, 'plants/plant_confirm_delete.html', {'plant': plant})

@login_required
def profile(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('plant')
    
    favorites_data = []
    for fav in favorites:
        plant = fav.plant
        
        watering_history = WateringLog.objects.filter(
            plant=plant,
            user=request.user
        ).order_by('-watered_at')
        
        favorites_data.append({
            'plant': plant,
            'watering_history': watering_history,
            'total_waterings': watering_history.count(),
        })
    
    return render(request, 'plants/profile.html', {
        'favorites_data': favorites_data,
        'today': date.today(),
    })

@login_required
def water_plant_toggle(request):
    if request.method == 'POST':
        plant_id = request.POST.get('plant_id')
        water_date = request.POST.get('water_date')
        
        plant = get_object_or_404(Plant, id=plant_id)
        
        WateringLog.objects.create(
            plant=plant,
            user=request.user,
            watered_at=water_date
        )
        
        if plant.last_watered is None or water_date > str(plant.last_watered):
            plant.last_watered = water_date
            plant.save()
        
        return redirect('profile')
    
    return redirect('profile')

@login_required
def toggle_favorite(request, pk):
    plant = get_object_or_404(Plant, id=pk)

    fav, created = Favorite.objects.get_or_create(
        user=request.user,
        plant=plant
    )

    if not created:
        fav.delete()

    return redirect(request.META.get('HTTP_REFERER', '/plants/'))
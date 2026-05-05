from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
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
        favorites = Favorite.objects.filter(user=request.user)\
            .values_list('plant_id', flat=True)

    return render(request, 'plants/plant_list.html', {
        'plants': plants,
        'favorites': favorites
    })

def plant_detail(request, pk):
    plant = Plant.objects.get(id=pk)
    return render(request, 'plants/plant_detail.html', {'plant': plant})

def plant_add(request):
    if request.method == 'POST':
        plant = Plant.objects.create(
            name=request.POST['name'],
            watering_frequency=int(request.POST['watering_frequency']),
            plant_type=request.POST['plant_type']
        )
        return render(request, 'plants/plant_detail.html', {'plant': plant})

    return render(request, 'plants/plant_form.html', {'plant': None})

def plant_edit(request, pk):
    plant = Plant.objects.get(id=pk)

    if request.method == 'POST':
        plant.name = request.POST['name']
        plant.watering_frequency = int(request.POST['watering_frequency'])
        plant.plant_type = request.POST['plant_type']

        plant.save()
        return render(request, 'plants/plant_detail.html', {'plant': plant})

    return render(request, 'plants/plant_form.html', {'plant': plant})

def plant_delete(request, pk):
    plant = Plant.objects.get(id=pk)
    plant.delete()
    plants = Plant.objects.all()
    return render(request, 'plants/plant_list.html', {'plants': plants})

@login_required
def profile(request):
    favorites = Favorite.objects.filter(user=request.user)
    watering_logs = WateringLog.objects.filter(user=request.user).order_by('-watered_at')[:10]

    return render(request, 'plants/profile.html', {
        'favorites': favorites,
        'watering_logs': watering_logs
    })

@login_required
def toggle_favorite(request, pk):
    plant = Plant.objects.get(id=pk)

    fav, created = Favorite.objects.get_or_create(
        user=request.user,
        plant=plant
    )

    if not created:
        fav.delete()

    return redirect(request.META.get('HTTP_REFERER', '/plants/'))
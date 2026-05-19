from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from django.contrib.auth import login as auth_login
from datetime import date, timedelta, datetime
from .models import Plant, WateringLog, Favorite

def get_notifications_for_user(user):
    if not user.is_authenticated:
        return []
    
    favorites = Favorite.objects.filter(user=user).select_related('plant')
    urgent_notifications = []
    upcoming_notifications = []
    
    for fav in favorites:
        plant = fav.plant
        days_left = plant.days_until_watering()
        next_date = plant.get_next_watering_date()
        
        if next_date and days_left is not None:
            if days_left <= 0:
                urgent_notifications.append({
                    'plant': plant,
                    'days_left': days_left,
                    'next_date': next_date
                })
            elif days_left <= 3:
                upcoming_notifications.append({
                    'plant': plant,
                    'days_left': days_left,
                    'next_date': next_date
                })
    
    urgent_notifications = sorted(urgent_notifications, key=lambda x: x['days_left'])
    upcoming_notifications = sorted(upcoming_notifications, key=lambda x: x['days_left'])
    all_notifications = urgent_notifications + upcoming_notifications
    return all_notifications[:10]

def home(request):
    notifications = []
    if request.user.is_authenticated:
        notifications = get_notifications_for_user(request.user)
    return render(request, 'plants/home.html', {'notifications': notifications})

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
    notifications = []
    if request.user.is_authenticated:
        favorites = Favorite.objects.filter(user=request.user).values_list('plant_id', flat=True)
        notifications = get_notifications_for_user(request.user)

    return render(request, 'plants/plant_list.html', {
        'plants': plants,
        'favorites': favorites,
        'notifications': notifications
    })

def plant_detail(request, pk):
    plant = get_object_or_404(Plant, id=pk)
    
    favorites = []
    user_watering_dates = []
    upcoming_watering_dates = []
    notifications = []
    
    if request.user.is_authenticated:
        favorites = Favorite.objects.filter(user=request.user).values_list('plant_id', flat=True)
        user_watering_logs = WateringLog.objects.filter(
            plant=plant,
            user=request.user
        )
        user_watering_dates = [log.watered_at.strftime('%Y-%m-%d') for log in user_watering_logs if log.watered_at]
        
        if plant.last_watered:
            watering_dates = plant.get_watering_dates(90)
            upcoming_watering_dates = []
            for d in watering_dates:
                upcoming_watering_dates.append({
                    'date': d,
                    'date_str': d.strftime('%Y-%m-%d'),
                    'is_watered': d.strftime('%Y-%m-%d') in user_watering_dates,
                    'is_past': d < date.today(),
                    'is_today': d == date.today()
                })
        
        notifications = get_notifications_for_user(request.user)
    
    return render(request, 'plants/plant_detail.html', {
        'plant': plant,
        'favorites': favorites,
        'user_watering_dates': user_watering_dates,
        'upcoming_watering_dates': upcoming_watering_dates,
        'today': date.today(),
        'notifications': notifications
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
    
    today = date.today()
    
    if request.method == 'POST' and 'water_plant_id' in request.POST:
        plant_id = request.POST.get('water_plant_id')
        water_date_str = request.POST.get('water_date')
        plant = get_object_or_404(Plant, id=plant_id)
        
        try:
            water_date = datetime.strptime(water_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return redirect('profile')
        
        existing = WateringLog.objects.filter(
            plant=plant,
            user=request.user,
            watered_at=water_date
        ).first()
        
        if existing:
            existing.delete()
        else:
            WateringLog.objects.create(
                plant=plant,
                user=request.user,
                watered_at=water_date
            )
            if plant.last_watered is None or water_date > plant.last_watered:
                plant.last_watered = water_date
                plant.save()
        
        return redirect('profile')
    
    favorites_data = []
    
    for fav in favorites:
        plant = fav.plant
        
        watering_history = WateringLog.objects.filter(
            plant=plant,
            user=request.user
        ).exclude(watered_at__isnull=True).order_by('-watered_at')
        
        next_water = plant.get_next_watering_date()
        days_left = plant.days_until_watering()
        
        favorites_data.append({
            'plant': plant,
            'watering_history': watering_history,
            'total_waterings': watering_history.count(),
            'next_watering': next_water,
            'days_left': days_left,
        })
    
    notifications = get_notifications_for_user(request.user)
    
    return render(request, 'plants/profile.html', {
        'favorites_data': favorites_data,
        'notifications': notifications,
        'today': today,
    })

@login_required
def water_plant_toggle(request):
    if request.method == 'POST':
        plant_id = request.POST.get('plant_id')
        water_date = request.POST.get('water_date')
        plant = get_object_or_404(Plant, id=plant_id)
        
        from datetime import datetime
        try:
            water_date = datetime.strptime(water_date, '%Y-%m-%d').date()
        except:
            from datetime import date
            water_date = date.today()
        
        existing = WateringLog.objects.filter(
            plant=plant,
            user=request.user,
            watered_at=water_date
        ).first()
        
        if existing:
            existing.delete()
        else:
            WateringLog.objects.create(
                plant=plant,
                user=request.user,
                watered_at=water_date
            )
            if plant.last_watered is None or water_date > plant.last_watered:
                plant.last_watered = water_date
                plant.save()
        
        return redirect('plant_detail', pk=plant.id)
    
    return redirect('plant_list')

@login_required
def toggle_favorite(request, pk):
    plant = get_object_or_404(Plant, id=pk)
    
    favorite = Favorite.objects.filter(user=request.user, plant=plant).first()
    
    if favorite:
        WateringLog.objects.filter(plant=plant, user=request.user).delete()
        favorite.delete()
    else:
        Favorite.objects.create(user=request.user, plant=plant)

    return redirect(request.META.get('HTTP_REFERER', '/plants/'))


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            from django.contrib.auth import login
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
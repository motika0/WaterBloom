from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('plants/', views.plant_list, name='plant_list'),
    path('plants/<int:pk>/', views.plant_detail, name='plant_detail'),
    path('plant/add/', views.plant_add, name='plant_add'),
    path('plant/<int:pk>/edit/', views.plant_edit, name='plant_edit'),
    path('plant/<int:pk>/delete/', views.plant_delete, name='plant_delete'),
    path('plant/<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('water-plant/', views.water_plant_toggle, name='water_plant_toggle'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
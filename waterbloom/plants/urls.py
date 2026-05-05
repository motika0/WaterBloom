from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('plants/', views.plant_list, name='plant_list'),
    path('plants/<int:pk>/', views.plant_detail, name='plant_detail'),
    path('plant/add/', views.plant_add, name='plant_add'),
    path('plant/<int:pk>/edit/', views.plant_edit, name='plant_edit'),
    path('plant/<int:pk>/delete/', views.plant_delete, name='plant_delete'),
    path('plant/<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('profile/', views.profile, name='profile'),

]
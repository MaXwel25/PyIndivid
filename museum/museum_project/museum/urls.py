from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('exhibition/<int:pk>/', views.exhibition_detail, name='exhibition_detail'),
    path('add/', views.add_exhibition, name='add_exhibition'),
    path('edit/<int:pk>/', views.edit_exhibition, name='edit_exhibition'),
    path('halls/', views.hall, name='hall_list'),  # Список залов
    path('hall/add/', views.add_hall, name='add_hall'),
    path('hall/edit/<int:pk>/', views.edit_hall, name='edit_hall'),
    path('hall/<int:pk>/', views.hall_detail, name='hall_detail')
]
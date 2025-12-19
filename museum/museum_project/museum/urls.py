from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('exhibition/<int:pk>/', views.exhibition_detail, name='exhibition_detail'),
    path('add/', views.add_exhibition, name='add_exhibition'),
    path('edit/<int:pk>/', views.edit_exhibition, name='edit_exhibition'),
]
from django.urls import path
from . import views

app_name = 'animals'

urlpatterns = [
    path('', views.AnimalListView.as_view(), name='animal_list'),
    path('<slug:slug>/', views.AnimalDetailView.as_view(), name='animal_detail'),
]

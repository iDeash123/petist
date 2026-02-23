from django.urls import path
from . import views

app_name = 'care'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('animal/<int:animal_id>/dashboard/', views.animal_care_dashboard, name='animal_dashboard'),
    path('animal/<int:animal_id>/task/add/', views.add_task, name='add_task'),
    path('task/<int:task_id>/toggle/', views.toggle_task, name='toggle_task'),
    path('task/<int:task_id>/delete/', views.delete_task, name='delete_task'),
]

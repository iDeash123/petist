from django.urls import path
from . import views

app_name = "animals"

urlpatterns = [
    path("manager/requests/", views.ManagerAdoptionRequestListView.as_view(), name="manager_requests"),
    path("manager/requests/<int:pk>/status/", views.manager_update_request_status, name="manager_request_status_update"),
    
    path("", views.AnimalListView.as_view(), name="animal_list"),
    path("<slug:slug>/", views.AnimalDetailView.as_view(), name="animal_detail"),
    path("toggle-favorite/<slug:slug>/", views.toggle_favorite, name="toggle_favorite"),
    path("toggle-adoption/<slug:slug>/", views.toggle_adoption, name="toggle_adoption"),
    path("start-adoption/<slug:slug>/", views.start_adoption, name="start_adoption"),
    path("start-favorite/<slug:slug>/", views.start_favorite, name="start_favorite"),
]

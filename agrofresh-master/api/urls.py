from django.urls import path, re_path
from api import views

app_name = "api"
urlpatterns = [
    path("cold_rooms/", views.cold_rooms, name="cold_rooms"),
    path("cold_rooms/historical/data/", views.historical_data, name="historical_data"),
    path("cold_rooms/historical/events/", views.historical_events, name="historical_events"),
    path("cold_rooms/<int:pk>/historical/data/", views.cold_room_data, name="cold_room_data"),
    path("cold_rooms/<int:pk>/historical/events/", views.cold_room_events, name="cold_room_events"),
    path("cold_rooms/<int:pk>/params/", views.cold_room_params, name="cold_room_params"),
]
from django.urls import path, re_path
from historical import views

app_name = "historical"
urlpatterns = [
    path("data", views.historical_data, name="data"),
    path("data_json", views.historical_data_json, name="data_json"),
    path("data_csv", views.historical_data_csv, name="data_csv"),
    path("events", views.EventsView.as_view(), name="events"),
    path("events_csv", views.EventsCsvView.as_view(), name="events_csv"),
    path("cold_rooms/<int:pk>/data/", views.cold_room_data, name="cold_room_data"),
    path("cold_rooms/<int:pk>/data_json/", views.cold_room_data_json, name="cold_room_data_json"),
    path("cold_rooms/<int:pk>/data_csv/", views.cold_room_data_csv, name="cold_room_data_csv"),
    # TODO path("cold_rooms/<int:pk>/events/", ????, name="cold_room_events"),
]

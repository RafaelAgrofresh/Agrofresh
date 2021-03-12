from django.urls import path
from cold_rooms import views

urlpatterns = [
    path('', views.cold_room_index, name='home'),
    path('cold_rooms', views.cold_room_index, name='cold_rooms'),
    path('cold_rooms/<int:pk>', views.cold_room_detail, name='cold_room_detail'),
    path('cold_rooms/<int:pk>/params', views.cold_room_params, name='cold_room_params'),
]

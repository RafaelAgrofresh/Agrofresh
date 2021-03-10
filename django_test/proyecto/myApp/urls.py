
#importamoss las vistas y las urls
from django.urls import path
from . import views



urlpatterns = [
    path('', views.visitas, name='home'),
    path('contacto', views.contacto, name='contacto'),
    path('upload', views.upload, name='upload')
]

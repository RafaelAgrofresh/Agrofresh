from django.contrib import admin

# importamos los modelos
from .models import Contacto

#importamos el modelo de Imagenes
from .models import Image

#regristramos el modelo en el administrador
admin.site.register(Image)
admin.site.register(Contacto)

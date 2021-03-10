
#imoortamos ls formularios de Django
from django import forms

#importamos nuestro modelo
from .models import Contacto

#importamos el modelo de imagen
from .models import Image


#creamos nuestro formularios
class ContactForm(forms.ModelForm):
    class Meta:
        #le decimos sobre que modelo va a trabajar
        model = Contacto

        #le decimos sobre que campos va a actuar
        fields = ("titulo","nombre", "mensaje",)


#creamos nuestro formularios
class ImageForm(forms.ModelForm):
    class Meta:
        #le decimos sobre que modelo va a trabajar
        model = Image

        #le decimos sobre que campos va a actuar
        fields = ("titulo","descripcion", "imagen",)

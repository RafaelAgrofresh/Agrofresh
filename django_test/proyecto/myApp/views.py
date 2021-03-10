from django.shortcuts import render, redirect

import datetime

#importamos nuestro modelo
from .models import Contacto

from .models import Image

#importamos nuestro formulario
from .forms import ContactForm

from .forms import ImageForm

#deifnimos nuestra vista de contacto
def contacto(request):

    #comprobamos que los datos se hallan enviado por el metodo post
    if request.method == "POST":
        contacto = ContactForm(request.POST)

        #definimos que hacer si nuestro formulario es valido
        if contacto.is_valid():
            contacto.save()
            #redirigimos a nuestro usuario al home
            return redirect('home')
    else:
        #en caso contrario dejamos nuestro formulario vacio
        contacto = ContactForm()


    #defimos los mismos campos en una variable separada por comodidad
    context={"contacto": contacto}

    #retornamos la vista
    return render(request, "contacto.html", context)

#deifnimos nuestra vista de contacto
def upload(request):

    #comprobamos que los datos se hallan enviado por el metodo post
    if request.method == "POST":
        imagen = ImageForm(request.POST , request.FILES)

        #definimos que hacer si nuestro formulario es valido
        if imagen.is_valid():
            imagen.save()
            #redirigimos a nuestro usuario al home
            return redirect('home')
    else:
        #en caso contrario dejamos nuestro formulario vacio
        imagen = ImageForm()


    #defimos los mismos campos en una variable separada por comodidad
    context={"imagen": imagen}

    #retornamos la vista
    return render(request, "imagen.html", context)


def visitas(request):
    imagenes= Image.objects.all().order_by('-id')
    context= {"image": imagenes}
    return render(request, "visitas.html", context)

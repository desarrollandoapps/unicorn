"""Unicorn URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Unicorn.views import borrardepartamento, borrarempleado, borrarempresa, detalleproceso, editardepartamento, editarempleado, entrenarred, index, ingresoempleado, ingresoempleado2, listadoempleados, logout, registrarempleado, registrarreclutador,registrarempresa,registrardepartamento,registrarproceso,indexreclutador,listadoempresa,listadodepartamento,ingresarlogin,editarempresa,listadoprocesos, registrarrespuestaempleado, finalempleado

urlpatterns = [
    path('',index),
    path('home',index),
    path('admin/', admin.site.urls),
    path('ingresar',ingresarlogin),
    path('registrese',registrarreclutador),
    path('salir',logout),
    path('indexreclutador',indexreclutador),
    path('registrarempresa',registrarempresa),
    path('listadoempresa',listadoempresa),
    path('borrarempresa/<int:id>',borrarempresa),
    path('editarempresa/<int:id>',editarempresa),
    path('registrardepartamento/<int:id>',registrardepartamento),
    path('listadodepartamento/<int:id>',listadodepartamento),
    path('editardepartamento/<int:id>', editardepartamento),
    path('borrardepartamento/<int:id>', borrardepartamento),
    path('listadoempleados/<int:id>',listadoempleados),
    path('registrarempleado/<int:id>',registrarempleado),
    path('editarempleado/<int:id>',editarempleado),
    path('borrarempleado/<int:id>',borrarempleado),
    path('registroproceso/<int:id>',registrarproceso),
    path('listadoprocesos',listadoprocesos),
    path('detalleproceso/<int:id>', detalleproceso),
    path('ingresoempleado/', ingresoempleado),
    path('ingresoempleado2/<int:id>', ingresoempleado2),
    path('registrarrespuestaempleado', registrarrespuestaempleado),
    path('finalempleado', finalempleado),
    path('entrenarred/<int:id>', entrenarred)
]

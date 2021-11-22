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
from Unicorn.views import borrardepartamento, borrarempresa, editardepartamento, index, registrarreclutador,registrarempresa,registrardepartamento,registrarproceso,indexreclutador,listadoempresa,listadodepartamento,ingresarlogin,editarempresa,listadoprocesos

urlpatterns = [
    path('',index),
    path('admin/', admin.site.urls),
    path('indexreclutador',indexreclutador),
    path('registrese',registrarreclutador),
    path('registrarempresa',registrarempresa),
    path('listadoempresa',listadoempresa),
    path('registrardepartamento/<int:id>',registrardepartamento),
    path('listadodepartamento/<int:id>',listadodepartamento),
    path('registroproceso/<int:id>',registrarproceso),
    path('listadoprocesos',listadoprocesos),
    path('ingresar',ingresarlogin),
    path('borrarempresa/<int:id>',borrarempresa),
    path('editarempresa/<int:id>',editarempresa),
    path('borrardepartamento/<int:id>', borrardepartamento),
    path('editardepartamento/<int:id>', editardepartamento)
]

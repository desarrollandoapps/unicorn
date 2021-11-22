from django import shortcuts
from django.db import connection, reset_queries
from django.shortcuts import render,redirect, resolve_url
from django.http import HttpResponse
from django.template import Template
from django.template.context import Context
from Unicorn.models import Reclutador,Empresa,Departamento,Proceso
from django.contrib.auth.models import User
from django.contrib import auth

#region index

def index(request):
    return render(request,"index.html")

#endregion

#region login

def ingresarlogin(request):
    if request.method=="POST":
        user = auth.authenticate(username = request.POST.get('email'), password = request.POST.get('contrasena'))
        if user is not None:
            auth.login(request, user)
            reclutador = Reclutador.objects.get(Email = request.user.email) 
            if reclutador is not None:
                # return redirect("Reclutador/index-reclutador.html")
                return redirect('/indexreclutador')
            else:
                return redirect('/')
        else:
            mensaje = "Usuario o contraseña incorrectos"
            return render(request, "Login/login.html", {'mensaje': mensaje})
    else:
        return render(request,"Login/login.html")



#endredion

#region empresa

def registrarempresa(request):
    if request.method=="POST":
        if request.POST.get('nombre'):
            empresa = Empresa()
            empresa.Nombre = request.POST.get('nombre')
            reclutador = Reclutador.objects.get(Email =request.user.email)
            empresa.reclutador_id = reclutador.id
            empresa.save()
            return redirect('/listadoempresa')
    else:
        return render(request,"Empresa/empresa.html")

def listadoempresa(request):
    reclutador = Reclutador.objects.get(Email =request.user.email) 
    empresas = Empresa.objects.all()
    return render(request,"Empresa/listadoempresa.html", {'empresas': empresas, 'reclutador': reclutador})

def borrarempresa(request, id):
    borrar = connection.cursor()
    strId = str(id)
    borrar.execute("call borrarempresa('" + strId + "')")
    return redirect('/listadoempresa')

def editarempresa(request, id):
    if request.method=="POST":
        if request.POST.get('nombre'):
            actualizar = connection.cursor()
            strId = str(id)
            actualizar.execute("call editarempresa('" + strId + "', '"+ request.POST.get('nombre') +"')")
            return redirect('/listadoempresa')
    else:
        empresa = Empresa.objects.filter(id = id)
        return render(request,"Empresa/editar.html", {'empresa': empresa})

#endregion

#region departamento

def registrardepartamento(request, id):
    empresa = Empresa.objects.get(id = id)
    reclutador = Reclutador.objects.get(Email = request.user.email)
    if request.method=="POST":
        if request.POST.get('nombre'):
            departamento = Departamento()
            departamento.Nombre = request.POST.get('nombre')
            departamento.Codigo = "1"
            strId = str(id)
            insertar = connection.cursor()
            insertar.execute("call registrardepartamento('"+departamento.Nombre+"','"+departamento.Codigo+"','"+ strId +"')")
            
            departamentos = Departamento.objects.filter(empresa_id = id)
            return render(request,"Departamento/listadodepartamento.html", {'deptos': departamentos, 'empresa': empresa})
    else:
        return render(request,"Departamento/departamento.html",{'empresa': empresa, 'reclutador': reclutador})

def listadodepartamento(request, id):
    empresa = Empresa.objects.get(id = id)
    departamentos = Departamento.objects.filter(empresa_id = id)
    return render(request,"Departamento/listadodepartamento.html", {'deptos': departamentos, 'empresa': empresa})

def borrardepartamento(request, id):
    depto = Departamento.objects.get(id = id)
    empresa = depto.empresa

    borrar = connection.cursor()
    strId = str(id)
    borrar.execute("call borrardepartamento('" + strId + "')")
    
    departamentos = Departamento.objects.filter(empresa_id = empresa.id)
    return render(request,"Departamento/listadodepartamento.html", {'deptos': departamentos, 'nombreEmpresa': empresa.Nombre})

def editardepartamento(request, id):
    depto = Departamento.objects.get(id = id)
    empresa = depto.empresa

    if request.method=="POST":
        if request.POST.get('nombre'):
            actualizar = connection.cursor()
            strId = str(id)
            actualizar.execute("call editardepartamento('" + strId + "', '"+ request.POST.get('nombre') +"')")
            depto = Departamento.objects.get(id = id)
            empresa = depto.empresa
            departamentos = Departamento.objects.filter(empresa_id = empresa.id)
            return render(request,"Departamento/listadodepartamento.html", {'deptos': departamentos, 'empresa': empresa})
    else:
        departamento = Departamento.objects.filter(id = id)
        return render(request,"Departamento/editar.html", {'departamento': departamento})

#endregion

#region proceso

def registrarproceso(request):
    return render(request,"Proceso/proceso.html")

def listarprocesos(request, id):
    empresa = Empresa.objects.get(id = id)
    departamentos = Departamento.objects.filter(empresa_id = id)
    
    return render(request, 'Proceso/listadoprocesos.html', {'deptos': departamentos, 'empresa': empresa})

#endregion


#region Reclutador

def indexreclutador(request):
    return render(request,"Reclutador/index-reclutador.html")


def registrarreclutador(request):
    if request.method=="POST":
        if request.POST.get('nombre') and request.POST.get('cargo') and request.POST.get('email') and request.POST.get('contrasena'):
            reclutador = Reclutador()
            reclutador.Nombre = request.POST.get('nombre')
            reclutador.Cargo = request.POST.get('cargo')
            reclutador.Email = request.POST.get('email')
            insertar = connection.cursor()
            insertar.execute("call registrarreclutador('"+reclutador.Nombre+"','"+reclutador.Cargo+"','"+reclutador.Email+"')")
            user = User.objects.create_user(request.POST.get('email'), request.POST.get('email'), request.POST.get('contrasena'))
            user.first_name = request.POST.get('nombre')
            user.save()
            return redirect("indexreclutador")
    else:
        return render(request,'registrese.html')

#endregion
from django import shortcuts
from django.db import connection, reset_queries
from django.shortcuts import render,redirect, resolve_url
from django.http import HttpResponse
from django.template import Template
from django.template.context import Context
from Unicorn.models import Reclutador,Empresa,Departamento,Proceso, Empleado
from django.contrib.auth.models import User
from django.contrib import auth
import random 
import string

#region index

def index(request):
    return render(request,"index.html")

#endregion

#region ingresar

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
    
def logout(request):
    auth.logout()
    return redirect('/index.html')
#endregion

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
    # empresa = Empresa.objects.all()
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

def registrarproceso(request,id):
    iddepartamento = str(id)
    if request.method=="POST":
        if request.POST.get('fechainicio') and request.POST.get('fechafin') and request.POST.get('cargo'):
            proceso = Proceso()
            proceso.FechaInicio = request.POST.get('fechainicio')
            proceso.FechaFin = request.POST.get('fechafin')
            proceso.Cargo = request.POST.get('cargo')
            estado = "En preparación"
            codigo = random_id()
            insertar = connection.cursor()
            insertar.execute("call registrarproceso('"+proceso.FechaInicio+"','"+proceso.FechaFin+"','"+estado+"','"+codigo+"','"+proceso.Cargo+"','"+iddepartamento+"')")
            return redirect("/listadoempresa")
    else:
        return render(request,"Proceso/proceso.html")

def listadoprocesos(request):
    departamentos = []
    procesos = []
    reclutador = Reclutador.objects.get(Email = request.user.email) 
    empresas = Empresa.objects.filter(reclutador_id=reclutador.id)
    for e in empresas:
        departamentos.append(Departamento.objects.filter(empresa_id = e.id))
    for d in departamentos:
        procesos.append(Proceso.objects.filter(departamento_id = d[0].id))
    procesos = sorted(procesos, key=lambda x: x[0].id)

    return render(request,"Proceso/listadoprocesos.html",{"empresas":empresas,"departamentos": departamentos, "procesos": procesos})

def random_id(lenght=6):
    return ''.join(random.choice(string.ascii_letters + string.digits) for x in range(lenght))

def detalleproceso(request, id):
    proceso = Proceso.objects.get(id = id)
    return render(request, "Proceso/detalleproceso.html", {"proceso": proceso})
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

#region Empleado
def registrarempleado(request):
    if request.method=="POST":
        if request.POST.get('nombre'):
            empleado = Empleado()
            empleado.Nombre = request.POST.get('nombre')
            empleado.Codigo = random_id()
            empleado.Estado = "Activo"
            empleado.save()
            return redirect('/listadoempleados')
    else:
        return render(request,'Empleado/empleado.html')

def listadoempleados(request, id):
    empleados = Empleado.objects.all().order_by('Nombre')
    return render(request, "Empleado/listadoempleados.html", {"empleados": empleados})

def borrarempleado(request, id):
    borrar = connection.cursor()
    strId = str(id)
    borrar.execute("call borrarempleado('" + strId + "')")
    return redirect('/listadoempleados/1')

def editarempleado(request, id):
    if request.method=="POST":
        if request.POST.get('nombre'):
            actualizar = connection.cursor()
            strId = str(id)
            actualizar.execute("call editarempleado('" + strId + "', '"+ request.POST.get('nombre') + "', '"+ request.POST.get('estado') +"')")
            return redirect('/listadoempleados/1')
    else:
        empleado = Empleado.objects.filter(id = id)
        return render(request,"Empleado/editar.html", {'empleado': empleado[0]})

def ingresoempleado(request):
    if request.method=="POST":
        if request.POST.get('codigo'):
            departamento = Departamento.objects.get(codigo = request.POST.get('codigo'))
            return redirect('/ingresoempleado2/'+ departamento)
    return render(request,"Empleado/ingreso.html")

def ingresoempleado2(request, id):
    return True

#endregion
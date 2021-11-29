from django import shortcuts
from django.db import connection, reset_queries
from django.shortcuts import render,redirect, resolve_url
from django.http import HttpResponse
from django.template import Template
from django.template.context import Context
from Unicorn.models import Reclutador,Empresa,Departamento,Proceso, Empleado, Respuesta, Respuesta_ADN
from django.contrib.auth.models import User
from django.contrib import auth
from django.db.models import Count
import random 
import string
import pandas as pd
from keras.models import Sequential
from keras.layers import Dense
import numpy
from tensorflow import keras

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
            departamento.Codigo = random_id()
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
            return redirect("/listadoprocesos")
    else:
        return render(request,"Proceso/proceso.html")

def listadoprocesos(request):
    departamentos = []
    procesos = []
    reclutador = Reclutador.objects.get(Email = request.user.email) 
    empresas = Empresa.objects.filter(reclutador_id=reclutador.id)
    for e in empresas:
        departamentos.append(Departamento.objects.filter(empresa_id = e.id))
    for depto in departamentos:
        for d in depto:
            procesos.append(Proceso.objects.filter(departamento_id = d.id))
    procesos = sorted(procesos, key=lambda x: x[0].id)

    return render(request,"Proceso/listadoprocesos.html",{"empresas":empresas,"departamentos": departamentos, "procesos": procesos})

def random_id(lenght=6):
    return ''.join(random.choice(string.ascii_letters + string.digits) for x in range(lenght))

def detalleproceso(request, id):
    proceso = Proceso.objects.get(id = id)
    respuestas = Respuesta_ADN.objects.filter(departamento_id = proceso.departamento_id)
    numResp = Respuesta_ADN.objects.all().distinct().values('empleado_id')
    numResp = len(numResp)
    return render(request, "Proceso/detalleproceso.html", {"proceso": proceso, "respuestas": respuestas, "numResp": numResp})

def entrenarred(request, id):
    proceso = Proceso.objects.get(id = id)
    # respuestas del departamento
    respuestas = Respuesta_ADN.objects.filter(departamento_id = proceso.departamento_id)
    # respuestas de diferentes empleados
    

    # Obtener los empleados por las repuestas
    idE = Respuesta_ADN.objects.distinct().values('empleado_id').filter(departamento_id = proceso.departamento_id)
    todasrespuestas = Respuesta_ADN.objects.filter(departamento_id = proceso.departamento_id)
    ids = []
    empleados = []

    for id1 in idE:
        ids.append(id1['empleado_id'])
    for id2 in ids:
        empleados.append(Empleado.objects.get(id = id2))
    amabilidad = 0
    gregarismo = 0
    asertividad = 0
    actividad = 0
    emociones = 0
    alegria = 0
    respuestasEmpleados = []
    x = []
    y = []
    # Promediar las respuestas por categoría por empleado
    for i in range(0, len(ids)):
        re = Respuesta_ADN.objects.filter(departamento_id = proceso.departamento_id).filter(empleado_id = ids[i]) # 60 respuestas de 1 empleado
        for resu in re:
            if resu.Categoria == "Amabilidad":
                amabilidad += int(resu.Factor) * int(resu.Respuesta)
            if resu.Categoria == "Gregarismo":
                gregarismo += int(resu.Factor) * int(resu.Respuesta)
            if resu.Categoria == "Asertividad":
                asertividad += int(resu.Factor) * int(resu.Respuesta)
            if resu.Categoria == "Nivel de Actividad":
                actividad += int(resu.Factor) * int(resu.Respuesta)
            if resu.Categoria == "Búsqueda de emociones":
                emociones += int(resu.Factor) * int(resu.Respuesta)
            if resu.Categoria == "Alegría":
                alegria += int(resu.Factor) * int(resu.Respuesta)
        respuestasEmpleados.append(amabilidad)
        respuestasEmpleados.append(gregarismo)
        respuestasEmpleados.append(asertividad) 
        respuestasEmpleados.append(actividad)
        respuestasEmpleados.append(emociones)
        respuestasEmpleados.append(alegria)
        x.append(respuestasEmpleados)
        amabilidad = 0
        gregarismo = 0
        asertividad = 0
        actividad = 0
        emociones = 0
        alegria = 0
        respuestasEmpleados = []
        if empleados[i].Estado == "Activo":
            y.append(1)
        else:
            y.append(0)
    # Crear dataset
    #ds = pd.DataFrame(y, columns = ['Amabilidad', 'Gregarismo', 'Asertividad', 'Nivel de actividad', 'Búsqueda de emociones', 'Alegría'])
    # crea el modelo
    model = Sequential()
    model.add(Dense(12, input_dim=6, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    # Compila el modelo
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    # Ajusta el modelo
    model.fit(x, y, epochs=150, batch_size=1)
    model.save('Unicorn/Public/models/modelo-reclutamiento.h5')
    return render(request, "Proceso/entrenared.html",{'idE': idE, 'respuestasEmpleados': x, "y":y})
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
def registrarempleado(request, id):
    if request.method=="POST":
        if request.POST.get('nombre'):
            depto = Departamento.objects.get(id = id)
            empleado = Empleado()
            empleado.Nombre = request.POST.get('nombre')
            empleado.Codigo = random_id()
            empleado.Estado = "Activo"
            empleado.departamento = depto
            empleado.save()
            strId = str(id)
            return redirect('/listadoempleados/' + strId)
    else:
        depto = Departamento.objects.get(id = id)
        return render(request,'Empleado/empleado.html', {"depto": depto})

def listadoempleados(request, id):
    depto = Departamento.objects.get(id = id)
    empleados = Empleado.objects.filter(departamento_id = id).order_by('Nombre')
    return render(request, "Empleado/listadoempleados.html", {"empleados": empleados, "depto": depto})

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
            try:
                departamento = Departamento.objects.get(Codigo = request.POST.get('codigo'))
                depto = str(departamento.id)
                return redirect('/ingresoempleado2/'+ depto)
            except:
                return render(request,"Empleado/ingreso.html", {"info": "El código no coincide. Intente de nuevo."})        
    else:
        return render(request,"Empleado/ingreso.html")

def ingresoempleado2(request, id):
    if request.method=="POST":
        if request.POST.get('codigo'):
            try:
                empleado = Empleado.objects.get(Codigo = request.POST.get('codigo'))
                return render(request,"Respuesta/index.html", {"empleado": empleado, "depto": id})
            except:
                return render(request,"Empleado/ingreso2.html", {"info": "El código no coincide. Intente de nuevo."})
    else:
        return render(request,"Empleado/ingreso2.html")

def registrarrespuestaempleado(request):
    if request.method=="POST":
        if request.POST.get('pregunta[]') and request.POST.get('categoria[]') and request.POST.get('factor[]') and request.POST.get('respuesta[]'):
            respuesta = Respuesta_ADN()
            preguntas = request.POST.getlist('pregunta[]')
            categorias = request.POST.getlist('categoria[]')
            factores = request.POST.getlist('factor[]')
            respuestas = request.POST.getlist('respuesta[]')
            depto = str(request.POST.get('depto'))
            empleado = str(request.POST.get('empleado'))
            for i in range(0, 60):
                guardar = connection.cursor()
                guardar.execute("call registrarrespuestasempleado('" + preguntas[i] + "', '" + categorias[i] + "', '"+ factores[i] + "', '" + respuestas[i] + "', '" + depto + "', '" + empleado + "')")
            return redirect("/finalempleado")
    else:
        return redirect('home')

def finalempleado(request):
    return render(request, "final-cuestionario-empleado.html")

#endregion

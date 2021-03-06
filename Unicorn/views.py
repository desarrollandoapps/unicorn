from django import shortcuts
from django.db import connection, reset_queries
from django.shortcuts import render,redirect, resolve_url
from django.http import HttpResponse
from django.template import Template
from django.template.context import Context
from Unicorn.models import Reclutador,Empresa,Departamento,Proceso, Empleado, Respuesta, Respuesta_ADN, Candidato
from django.contrib.auth.models import User
from django.contrib import auth
from django.db.models import Count
import random 
import string
# import pandas as pd
# from keras.models import Sequential
# from keras.layers import Dense
# import numpy
# from tensorflow import keras

#region index

def index(request):
    try:
        candidato = Candidato.objects.get(Email = request.user.email)
        return render(request,"index.html", {'candidato': candidato})
    except:
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

def logincandidato(request):
    if request.method=="POST":
        user = auth.authenticate(username = request.POST.get('email'), password = request.POST.get('contrasena'))
        if user is not None:
            auth.login(request, user)
            candidato = Candidato.objects.get(Email = request.user.email)
            if candidato is not None:
                return redirect('/ingresocandidato2/'+ str(candidato.id))
            else:
                return redirect('/')
        else:
            mensaje = "Usuario o contraseña incorrectos"
            return render(request, "Login/logincandidato.html", {'mensaje': mensaje})
    else:
        return render(request,"Login/logincandidato.html")

def logout(request):
    auth.logout(request)
    return redirect('/')
#endregion

#region Empresa

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

#region Departamento

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

#region Proceso

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
    departamento = proceso.departamento_id
    if proceso.Estado == "En preparación":
        # respuestas del departamento
        respuestas = Respuesta_ADN.objects.filter(departamento_id = departamento)
        # Obtener los empleados por las repuestas
        idE = Respuesta_ADN.objects.distinct().values('empleado_id').filter(departamento_id = departamento)
        todasrespuestas = Respuesta_ADN.objects.filter(departamento_id = departamento)
        ids = []
        for id1 in idE:
            ids.append(id1['empleado_id'])
        numResp = len(ids)
        return render(request, "Proceso/detalleproceso.html", {"proceso": proceso, "numResp": numResp})
    #elif proceso.Estado == "Iniciado":
        # Respuestas de candidatos
        #return render(request, "Proceso/detalleproceso.html", {"proceso": proceso, "numResp": numResp})

def entrenarred(request, id):
    return True
#     proceso = Proceso.objects.get(id = id)
#     departamento = proceso.departamento_id
#     # respuestas del departamento
#     respuestas = Respuesta_ADN.objects.filter(departamento_id = departamento)
#     # Obtener los empleados por las repuestas
#     idE = Respuesta_ADN.objects.distinct().values('empleado_id').filter(departamento_id = departamento)
#     todasrespuestas = Respuesta_ADN.objects.filter(departamento_id = departamento)
#     ids = []
#     empleados = []

#     for id1 in idE:
#         ids.append(id1['empleado_id'])
#     for id2 in ids:
#         empleados.append(Empleado.objects.get(id = id2))
#     amabilidad = 0
#     gregarismo = 0
#     asertividad = 0
#     actividad = 0
#     emociones = 0
#     alegria = 0
#     respuestasEmpleados = []
#     x = []
#     y = []
#     # Promediar las respuestas por categoría por empleado
#     for i in range(0, len(ids)):
#         re = Respuesta_ADN.objects.filter(departamento_id = departamento).filter(empleado_id = ids[i]) # 60 respuestas de 1 empleado
#         for resu in re:
#             if resu.Categoria == "Amabilidad":
#                 amabilidad += int(resu.Factor) * int(resu.Respuesta)
#             if resu.Categoria == "Gregarismo":
#                 gregarismo += int(resu.Factor) * int(resu.Respuesta)
#             if resu.Categoria == "Asertividad":
#                 asertividad += int(resu.Factor) * int(resu.Respuesta)
#             if resu.Categoria == "Nivel de Actividad":
#                 actividad += int(resu.Factor) * int(resu.Respuesta)
#             if resu.Categoria == "Búsqueda de emociones":
#                 emociones += int(resu.Factor) * int(resu.Respuesta)
#             if resu.Categoria == "Alegría":
#                 alegria += int(resu.Factor) * int(resu.Respuesta)
#         respuestasEmpleados.append(amabilidad)
#         respuestasEmpleados.append(gregarismo)
#         respuestasEmpleados.append(asertividad) 
#         respuestasEmpleados.append(actividad)
#         respuestasEmpleados.append(emociones)
#         respuestasEmpleados.append(alegria)
#         x.append(respuestasEmpleados)
#         amabilidad = 0
#         gregarismo = 0
#         asertividad = 0
#         actividad = 0
#         emociones = 0
#         alegria = 0
#         respuestasEmpleados = []
#         if empleados[i].Estado == "Activo":
#             y.append(1)
#         else:
#             y.append(0)
#     # Crea el modelo
#     model = Sequential()
#     model.add(Dense(12, input_dim=6, activation='relu'))
#     model.add(Dense(1, activation='sigmoid'))
#     # Compila el modelo
#     model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
#     # Ajusta el modelo
#     model.fit(x, y, epochs=150, batch_size=1)
#     # Guarda el modelo
#     model.save('Unicorn/Public/models/modelo' + str(departamento) + '.h5')
#     # Cambiar el estado del proceso
#     cambiarEstadoProceso(id, "Iniciado")
#     proceso = Proceso.objects.get(id = id)
#     return render(request, "Proceso/entrenared.html",{'idE': idE, 'respuestasEmpleados': x, "y":y, "proceso": proceso})

def cambiarEstadoProceso(idProceso, estado):
    actualizar = connection.cursor()
    strId = str(idProceso)
    actualizar.execute("call cambiarEstadoProceso('" + strId + "', '"+ estado +"')")
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
            return redirect("/indexreclutador")
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
        return redirect('/home')

def finalempleado(request):
    return render(request, "final-cuestionario-empleado.html")

#endregion

#region Candidato

def ingresoCandidato(request):
    
    if request.user.is_authenticated:
        candidato = Candidato.objects.get(Email = request.user.email)
        return redirect('/ingresocandidato2/' + str(candidato.id))
    else:
        #LLevar a registro de candidato
        return redirect('/logincandidato')

def ingresocandidato2(request, id):
    if request.method=="POST":
        if request.POST.get('codigo'):
            candidato = Candidato.objects.get(id = id)
            try:
                proceso = Proceso.objects.get(Codigo = request.POST.get('codigo'))
                return render(request,"Respuesta/respuesta-candidato.html", {"candidato": candidato, "proceso": proceso})
            except:
                return render(request,"Candidato/ingreso2.html", {"info": "El código no coincide. Intente de nuevo."})
    else:
        return render(request,"Candidato/ingreso2.html")
    
def registrarCandidato(request):
    if request.method=="POST":
        if request.POST.get('nombre') and request.POST.get('edad') and request.POST.get('estadocivil') and request.POST.get('genero') and request.POST.get('escolaridad') and request.POST.get('residencia') and request.POST.get('personashogar') and request.POST.get('hijos') and request.POST.get('mascotas') and request.POST.get('talla') and request.POST.get('peso') and request.POST.get('email') and request.POST.get('celular') and request.POST.get('contrasena') and request.POST.get('estrato'):
            candidato = Candidato()
            candidato.Nombre = request.POST.get('nombre')
            candidato.Edad = request.POST.get('edad')
            candidato.EstadoCivil = request.POST.get('estadocivil')
            candidato.Estrato = request.POST.get('estrato')
            candidato.Genero = request.POST.get('genero')
            candidato.NivelEscolar = request.POST.get('escolaridad')
            candidato.Residencia = request.POST.get('residencia')
            candidato.PersonasHogar = request.POST.get('personashogar')
            candidato.Hijos = request.POST.get('hijos')
            candidato.Mascotas = request.POST.get('mascotas')
            imc = int(request.POST.get('peso')) / ((int(request.POST.get('talla')) * int(request.POST.get('talla')))/10000)
            candidato.Imc = imc
            candidato.Email = request.POST.get('email')
            candidato.Celular = request.POST.get('celular')
            candidato.save()
            
            user = User.objects.create_user(request.POST.get('email'), request.POST.get('email'), request.POST.get('contrasena'))
            user.first_name = request.POST.get('nombre')
            user.save()
            return redirect("/logincandidato")
    else:
        return render(request,'registro-candidato.html')

def registrarrespuestacandidato(request):
    if request.method=="POST":
        if request.POST.get('pregunta[]') and request.POST.get('categoria[]') and request.POST.get('factor[]') and request.POST.get('respuesta[]'):
            respuesta = Respuesta()
            preguntas = request.POST.getlist('pregunta[]')
            categorias = request.POST.getlist('categoria[]')
            factores = request.POST.getlist('factor[]')
            respuestas = request.POST.getlist('respuesta[]')
            depto = str(request.POST.get('depto'))
            empleado = str(request.POST.get('empleado'))
            for i in range(0, 60):
                guardar = connection.cursor()
                #### OJO ######
                guardar.execute("call registrarrespuestascandidato('" + preguntas[i] + "', '" + categorias[i] + "', '"+ factores[i] + "', '" + respuestas[i] + "', '" + depto + "', '" + empleado + "')")
            return redirect("/finalempleado")
    else:
        return redirect('/home')
#endregion
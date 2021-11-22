from django.db import models
from django.db.models.deletion import PROTECT

class Reclutador(models.Model):
    Nombre=models.CharField(max_length=255)
    Cargo=models.CharField(max_length=255)
    Email=models.CharField(max_length=255)
    class Meta:
        db_table = "reclutador"

class Empleado(models.Model):
    Nombre=models.CharField(max_length=255)
    Codigo=models.CharField(max_length=255)
    Estado=models.CharField(max_length=255)
    class Meta:
        db_table = "empleado"

class Empresa(models.Model):
    Nombre=models.CharField(max_length=255)
    reclutador=models.ForeignKey(Reclutador,on_delete=models.PROTECT)
    class Meta:
        db_table = "empresa"

class Departamento(models.Model):
    Nombre=models.CharField(max_length=255)
    Codigo=models.CharField(max_length=255)
    empresa=models.ForeignKey(Empresa,on_delete=models.PROTECT)
    class Meta:
        db_table = "departamento"

class Respuesta_ADN(models.Model):
    Pregunta=models.CharField(max_length=255)
    Categoria=models.CharField(max_length=255)
    Factor=models.CharField(max_length=255)
    Respuesta=models.CharField(max_length=255)
    departamento=models.ForeignKey(Departamento,on_delete=models.PROTECT)
    empresa=models.ForeignKey(Empresa,on_delete=models.PROTECT)
    class Meta:
        db_table = "respuesta_adn"

class Proceso(models.Model):
    FechaInicio=models.CharField(max_length=255)
    FechaFin=models.CharField(max_length=255)
    Estado=models.CharField(max_length=255)
    Codigo=models.CharField(max_length=255)
    Cargo=models.CharField(max_length=255)
    departamento=models.ForeignKey(Departamento,on_delete=models.PROTECT)
    class Meta:
        db_table = "proceso"
class Candidato(models.Model):
    Nombre=models.CharField(max_length=255)
    Edad=models.CharField(max_length=255)
    EstadoCivil=models.CharField(max_length=255)
    Estrato=models.CharField(max_length=255)
    NivelEscolar=models.CharField(max_length=255)
    Genero=models.CharField(max_length=255)
    PersonasHogar=models.CharField(max_length=255)
    Residencia=models.CharField(max_length=255)
    Hijos=models.CharField(max_length=255)
    Mascotas=models.CharField(max_length=255)
    Imc=models.CharField(max_length=255)
    GastoTransporte=models.CharField(max_length=255)
    Email=models.CharField(max_length=255)
    Celular=models.CharField(max_length=255)
    class Meta:
        db_table = "candidato"

class Respuesta(models.Model):
    Pregunta=models.CharField(max_length=255)
    Categoria=models.CharField(max_length=255)
    Factor=models.CharField(max_length=255)
    Respuesta=models.CharField(max_length=255)
    candidato=models.ForeignKey(Candidato,on_delete=models.PROTECT)
    proceso=models.ForeignKey(Proceso,on_delete=models.PROTECT)
    class Meta:
        db_table = "respuesta"


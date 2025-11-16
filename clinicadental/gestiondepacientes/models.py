from django.db import models

from gestionespecialistas.models import Especialista
from gestiontratamientos.models import Tratamiento

# Create your models here.

class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dui = models.CharField(unique=True, max_length=10, blank=True, null=True)
    correo = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    fecha_ingreso = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'paciente'



class PacienteTratamiento(models.Model):
    paciente = models.ForeignKey(Paciente, models.DO_NOTHING)
    tratamiento = models.ForeignKey(Tratamiento, models.DO_NOTHING)
    especialista = models.ForeignKey(Especialista, models.DO_NOTHING, blank=True, null=True)
    fecha_inicio = models.DateTimeField(blank=True, null=True)
    fecha_fin = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=11, blank=True, null=True)
    notas = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'paciente_tratamiento'


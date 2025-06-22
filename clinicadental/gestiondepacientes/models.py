from django.db import models

# Create your models here.
class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dui = models.CharField(max_length=10, unique=True)
    fecha_ingreso = models.DateField()
    correo = models.CharField(max_length=20)
    telefono = models.CharField(max_length=20)
    
    def __str__(self):
        return self.nombre
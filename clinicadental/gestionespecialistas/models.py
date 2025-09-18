from django.db import models

# Create your models here.

class Especialista(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.CharField(max_length=100, blank=True, null=True)
    dui = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        db_table = 'especialista'

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

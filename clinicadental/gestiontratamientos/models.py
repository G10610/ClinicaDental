from django.db import models

# Create your models here.

class Tratamiento(models.Model):

    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    costo_referencia = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    duracion_minutos = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'tratamiento'

    def __str__(self):
        return self.nombre 


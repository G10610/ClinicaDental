from django.db import models


class Cita(models.Model):
    fecha_hora = models.DateTimeField()
    paciente = models.ForeignKey('gestiondepacientes.Paciente', on_delete=models.CASCADE)
    especialista = models.ForeignKey('gestionespecialistas.Especialista', on_delete=models.SET_NULL, blank=True, null=True)
    tratamiento = models.ForeignKey('gestiontratamientos.Tratamiento', on_delete=models.SET_NULL, blank=True, null=True)
    estado = models.CharField(max_length=10, blank=True, null=True)
    detalles = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'cita'
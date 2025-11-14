from django.db import models

class ConfiguracionClinica(models.Model):
    INTERVALOS_CITA = [
        (10, '10 minutos'),
        (15, '15 minutos'),
        (30, '30 minutos'),
        (60, '1 hora'),
    ]

    DIAS_LABORALES = [
        ('0,1,2,3,4,5', 'Lunes a Sábado'),
        ('0,1,2,3,4', 'Lunes a Viernes'),
        ('0,1,2,3,4,5,6', 'Toda la semana'),
    ]

    hora_apertura = models.TimeField(default='08:00:00')
    hora_cierre = models.TimeField(default='18:00:00')
    intervalo_citas = models.IntegerField(choices=INTERVALOS_CITA, default=30)
    dias_laborales = models.CharField(max_length=20, choices=DIAS_LABORALES, default='0,1,2,3,4,5')

    def get_dias_laborales_lista(self):
        """Convierte el string '0,1,2,3,4' en [0,1,2,3,4]"""
        if not self.dias_laborales:
            return []
        return [int(x) for x in str(self.dias_laborales).split(',')]

    def __str__(self):
        return "Configuración de la Clínica"

    class Meta:
        verbose_name_plural = "Configuración de la Clínica"

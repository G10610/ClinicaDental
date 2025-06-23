from django.forms import ModelForm
from .models import Paciente

class CrearPacienteForm(ModelForm):
    class Meta:
        model = Paciente
        fields = ['nombre','apellido','dui','fecha_ingreso','correo','telefono']
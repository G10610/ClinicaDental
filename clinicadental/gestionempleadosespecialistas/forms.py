from django.forms import ModelForm
from .models import Empleado

class CrearEmpleadoForm(ModelForm):
    class Meta:
        model = Empleado
        fields = ['nombre','apellido','dui','fecha_ingreso','salario','telefono']


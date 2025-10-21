from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


from .models import Paciente

# Validadores de servidor seguridad extra
dui_validator = RegexValidator(
    regex=r'^\d{8}-\d$',
    message='El DUI debe tener el formato 12345678-9'
)
solo_letras_validator = RegexValidator(
    regex=r'^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$',
    message='Este campo solo puede contener letras y espacios'
)
telefono_validator = RegexValidator(
    regex=r'^\+?\d[\d\- ]{7,14}$',
    message='El teléfono debe tener entre 8 y 15 caracteres, solo números, espacios o guiones.'
)

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['nombre','apellido','dui','fecha_ingreso','correo','telefono','direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'pattern': r'^[A-Za-zÁÉÍÓÚáéíóúñÑ\s]+$',
                'title': 'Solo se permiten letras'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'pattern': r'^[A-Za-zÁÉÍÓÚáéíóúñÑ\s]+$',
                'title': 'Solo se permiten letras'
            }),
            'dui': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': '12345678-9',
                'pattern': r'\d{8}-\d',
                'title': '8 dígitos, guion y 1 dígito (12345678-9)'
            }),
            'fecha_ingreso': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'usuario@dominio.com'}),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'tel',
                'placeholder': '+503 1234-5678',    
                'pattern': r'^\+?\d[\d\- ]{7,14}$',
                'title': 'Solo números, espacios o guiones',
            }),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
        }

    #Campos no obligatorios
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_ingreso'].required = False
        self.fields['correo'].required = False
        self.fields['telefono'].required = False
        self.fields['direccion'].required = False

    # forms.py
    def clean_dui(self):
        dui = self.cleaned_data['dui']
        qs = Paciente.objects.filter(dui=dui)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)  # ignorar el paciente actual
        if qs.exists():
            raise forms.ValidationError('Ya existe un paciente con ese DUI.')
        return dui


    def clean_fecha_ingreso(self):
        fecha = self.cleaned_data.get('fecha_ingreso')
        if fecha and fecha > timezone.localdate():  # se usa la fecha local según TIME_ZONE del settings.py
            raise forms.ValidationError('La fecha de ingreso no puede ser futura.')
        return fecha
    
    

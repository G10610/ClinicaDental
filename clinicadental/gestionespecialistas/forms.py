from django import forms
from .models import Especialista
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

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

class CrearEspecialistaForm(forms.ModelForm):
    class Meta:
        model = Especialista
        fields = ['nombre','apellido','dui','especialidad','correo','telefono']
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
            'especialidad': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'pattern': r'^[A-Za-zÁÉÍÓÚáéíóúñÑ\s]+$',
                'title': 'Solo se permiten letras'
            }),
        
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'usuario@dominio.com'}),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'tel',
                'placeholder': '+503 1234-5678',    
                'pattern': r'^\+?\d[\d\- ]{7,14}$',
                'title': 'Solo números, espacios o guiones',
            }),
        }

    #Campos no obligatorios
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['correo'].required = False
        self.fields['telefono'].required = False
        
    # forms.py
    def clean_dui(self):
        dui = self.cleaned_data['dui']
        qs = Especialista.objects.filter(dui=dui)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)  # ignorar el especialista actual
        if qs.exists():
            raise forms.ValidationError('Ya existe un especialista con ese DUI.')
        return dui

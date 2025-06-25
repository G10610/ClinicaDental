from django import forms
from .models import Paciente
from django.core.validators import RegexValidator

dui_validator = RegexValidator(
    regex=r'^\d{8}-\d$',
    message='El DUI debe tener el formato 12345678-9'
)


class CrearPacienteForm(forms.ModelForm):
        dui = forms.CharField(
        max_length=10,
        validators=[dui_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12345678-9',
            'pattern': r'\d{8}-\d',
            'title': '8 dígitos, guion y 1 dígito (12345678-9)'
        }),
        help_text='Ingrese el DUI en formato 12345678-9'
        )
        class Meta:
         model = Paciente
         fields = ['nombre','apellido','dui','fecha_ingreso','correo','telefono']
         widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_ingreso': forms.DateInput(attrs={'class': 'form-control','type': 'date'}, format='%Y-%m-%d'),
            'correo': forms.TextInput(attrs={'class': 'form-control','type': 'email','pattern': r'[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}$',
            'title': 'Formato: usuario@dominio.ext',}),
            'telefono': forms.TextInput(attrs={'class': 'form-control','type': 'tel','placeholder': '+503 1234‑5678'}),
        }

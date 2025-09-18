from django import forms
from .models import Especialista
from django.core.validators import RegexValidator

dui_validator = RegexValidator(
    regex=r'^\d{8}-\d$',
    message='El DUI debe tener el formato 12345678-9'
)


class CrearEspecialistaForm(forms.ModelForm):

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
        model = Especialista
        fields = ['nombre', 'apellido', 'dui', 'especialidad', 'correo', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'dui': forms.TextInput(attrs={'class': 'form-control', }),
            'especialidad': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'type': 'tel', 'placeholder': '+503 1234‑5678'}),
        }

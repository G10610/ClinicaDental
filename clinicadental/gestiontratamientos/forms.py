from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


from .models import Tratamiento

# Validadores de servidor seguridad extra




class TratamientoForm(forms.ModelForm):
    class Meta:
        model = Tratamiento
        fields = ['nombre','descripcion','costo_referencia','duracion_minutos']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'pattern': r'^[A-Za-zÁÉÍÓÚáéíóúñÑ\s]+$',
                'title': 'Solo se permiten letras'
            }),
            'descripcion': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
            }),
            'costo_referencia': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': '$',
                'pattern': r'(5000(\.0+)?|([1-4]?\d{1,3}|\d)(\.\d+)?)$',
                'title': 'Solo enteros o decimales'
            }),

            'duracion_minutos': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': 'Escriba el numero de minutos',    
                'pattern': r'([1-9][0-9]{0,2}|[1-4][0-9]{3}|5000)$',
                'title': 'Solo números enteros',
            }),

        }

    #Campos no obligatorios
    #def __init__(self, *args, **kwargs):
        #super().__init__(*args, **kwargs)
        #self.fields['fecha_ingreso'].required = False
        #self.fields['correo'].required = False
        #self.fields['telefono'].required = False
        #self.fields['direccion'].required = False



    # forms.py
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        qs = Tratamiento.objects.filter(nombre=nombre)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)  # ignorar el tratamiento actual
        if qs.exists():
            raise forms.ValidationError('Ya existe un tratamiento con ese nombre.')
        return nombre


    #def clean_fecha_ingreso(self):
        #fecha = self.cleaned_data.get('fecha_ingreso')
        #if fecha and fecha > timezone.localdate():  # se usa la fecha local según TIME_ZONE del settings.py
            #raise forms.ValidationError('La fecha de ingreso no puede ser futura.')
        #return fecha
from django import forms
from .models import ConfiguracionClinica

class ConfiguracionForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionClinica
        fields = ['hora_apertura', 'hora_cierre', 'intervalo_citas', 'dias_laborales']
        
        # Aquí aplicamos las clases de Bootstrap a los campos
        widgets = {
            'hora_apertura': forms.TimeInput(
                attrs={'class': 'form-control', 'type': 'time'}
            ),
            'hora_cierre': forms.TimeInput(
                attrs={'class': 'form-control', 'type': 'time'}
            ),
            'intervalo_citas': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'dias_laborales': forms.Select(
                attrs={'class': 'form-select'}),
        }
        
        # (Opcional) Etiquetas más amigables
        labels = {
                'hora_apertura': 'Mostrar agenda desde las',
                'hora_cierre': 'Mostrar agenda hasta las',
                'intervalo_citas': 'Intervalo de los espacios',
                'dias_laborales': 'Días a mostrar en la agenda',
            }
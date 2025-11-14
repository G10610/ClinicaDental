from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import ConfiguracionClinica
from .forms import ConfiguracionForm

@login_required
def gestionar_configuracion(request):
    
    # Intentamos obtener la configuración (ID=1). 
    # Si no existe, la creamos.
    config, created = ConfiguracionClinica.objects.get_or_create(id=1)

    if request.method == 'POST':
        form = ConfiguracionForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Configuración guardada exitosamente!')
            return redirect('gestionar_configuracion') # Recargamos la misma pág.
    else:
        # Mostramos el formulario con los datos actuales
        form = ConfiguracionForm(instance=config)

    context = {
        'form': form
    }
    return render(request, 'configuracion.html', context)
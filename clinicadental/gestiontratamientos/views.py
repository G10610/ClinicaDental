from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .forms import TratamientoForm
from django.contrib.auth.decorators import login_required
from . models import Tratamiento

# funciones de gestion CRUD


# Listar tratamientos
@login_required
def lista_tratamientos(request):
    """Muestra la lista completa de tratamientos."""
    tratamiento = Tratamiento.objects.all().order_by('nombre')
    return render(request, "listatratamiento.html", {"tratamiento": tratamiento})





#crear tratamiento
@login_required
def crear_tratamiento(request):
    if request.method == 'POST':
        form = TratamientoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_tratamientosss')
    else:
        form = TratamientoForm()
    return render(request, 'creartratamiento.html', {'form': form})






#**Editar paciente**

# GET: Carga los datos del paciente en el formulario de edición
@login_required
def edicionTratamiento(request, id):
  tratamiento = Tratamiento.objects.get(id=id)
  return render(request, "ediciontratamiento.html", {"tratamiento": tratamiento})

# POST: Recibe los datos del formulario y actualiza el registro en la base de datos
@login_required
def editarTratamiento(request):
    
    tratamiento_id= request.POST['id']
    nombre = request.POST['nombre']
    descripcion = request.POST['descripcion']
    costo_referencia = request.POST['costo_referencia']
    duracion_minutos = request.POST['duracion_minutos']


    tratamiento = Tratamiento.objects.get(id=tratamiento_id)
    tratamiento.nombre = nombre
    tratamiento.descripcion = descripcion
    tratamiento.costo_referencia = costo_referencia
    tratamiento.duracion_minutos = duracion_minutos

    tratamiento.save()
    return redirect('lista_tratamientosss')






# eliminar paciente
@login_required
def eliminar_tratamiento(request, id):
    """Elimina un tratamiento específico."""
    tratamiento = get_object_or_404(Tratamiento, pk=id) # También se recomienda usar get_object_or_404 aquí
    tratamiento.delete()
    return redirect('lista_tratamientosss')

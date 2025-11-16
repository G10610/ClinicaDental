from django.shortcuts import render, redirect, get_object_or_404
from .forms import CrearEspecialistaForm
from django.contrib.auth.decorators import login_required
from . models import Especialista
# Create your views here.


#crear especialista

@login_required
def listae(request):
    """Muestra la lista completa de especialistas."""
    especialistas = Especialista.objects.all().order_by('apellido', 'nombre')
    return render(request, "listaEspecialistas.html", {"especialistas": especialistas})

#crear especialista
@login_required
def crear_especialista(request):
    if request.method == 'POST':
        form = CrearEspecialistaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listae')
    else:
        form = CrearEspecialistaForm()
    return render(request, 'crearespecialistas.html', {'form': form})

@login_required
def edicionEspecialista(request, id):
  especialista = Especialista.objects.get(id=id)
  return render(request, "edicionEspecialista.html", {"especialista": especialista})

# POST: Recibe los datos del formulario y actualiza el registro en la base de datos
@login_required
def editarEspecialista(request):
    
    especialista_id= request.POST['id']
    nombre = request.POST['nombre']
    apellido = request.POST['apellido']
    especialidad = request.POST['especialidad']
    telefono = request.POST['telefono']
    correo = request.POST['correo']
    dui = request.POST['dui']

    especialista = Especialista.objects.get(id=especialista_id)
    especialista.nombre = nombre
    especialista.apellido = apellido
    especialista.especialidad = especialidad
    especialista.correo = correo
    especialista.telefono = telefono
    especialista.dui = dui

    especialista.save()
    return redirect('listae')


# eliminar especialista
@login_required
def eliminar_especialista(request, id):
    """Elimina un especialista específico."""
    especialista = get_object_or_404(Especialista, pk=id) # También se recomienda usar get_object_or_404 aquí
    especialista.delete()
    return redirect('listae')


from django.shortcuts import render, redirect, get_object_or_404
from .forms import PacienteForm
from django.contrib.auth.decorators import login_required
from . models import Paciente

# funciones de gestion CRUD

@login_required
def crudpacientes(request):
    """Muestra la página principal de gestión de pacientes (dashboard o menú)."""
    return render(request, 'gestionpacientes.html')

@login_required
def lista(request):
    """Muestra la lista completa de pacientes."""
    pacientes = Paciente.objects.all().order_by('apellido', 'nombre')
    return render(request, "listaPacientes.html", {"pacientes": pacientes})

#crear paciente
@login_required
def crear_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista')
    else:
        form = PacienteForm()
    return render(request, 'crearpacientes.html', {'form': form})

#**Editar paciente**

# GET: Carga los datos del paciente en el formulario de edición
@login_required
def edicionPaciente(request, id):
  paciente = Paciente.objects.get(id=id)
  return render(request, "edicionPaciente.html", {"paciente": paciente})

# POST: Recibe los datos del formulario y actualiza el registro en la base de datos
@login_required
def editarPaciente(request):
    
    paciente_id= request.POST['id']
    nombre = request.POST['nombre']
    apellido = request.POST['apellido']
    dui = request.POST['dui']
    fecha_ingreso = request.POST['fecha_ingreso']
    correo = request.POST['correo']
    telefono = request.POST['telefono']
    direccion = request.POST['direccion']

    paciente = Paciente.objects.get(id=paciente_id)
    paciente.nombre = nombre
    paciente.apellido = apellido
    paciente.dui = dui
    paciente.fecha_ingreso = fecha_ingreso
    paciente.correo = correo
    paciente.telefono = telefono
    paciente.direccion = direccion

    paciente.save()
    return redirect('lista')


# eliminar paciente
@login_required
def eliminar_paciente(request, id):
    """Elimina un paciente específico."""
    paciente = get_object_or_404(Paciente, pk=id) # También se recomienda usar get_object_or_404 aquí
    paciente.delete()
    return redirect('lista')
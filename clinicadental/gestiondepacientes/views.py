from django.shortcuts import render, redirect, get_object_or_404
from .forms import PacienteForm
from django.contrib.auth.decorators import login_required
from . models import Paciente

from .models import Paciente, PacienteTratamiento
from .forms import ExpedienteForm

# funciones de gestion CRUD


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






#EXPEDINETE DE PACIENTE
def expediente_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    # Obtener todos los expedientes del paciente
    expedientes = PacienteTratamiento.objects.filter(
        paciente=paciente
    ).select_related('tratamiento', 'especialista')
    
    # Formulario para agregar nuevo tratamiento al paciente
    if request.method == 'POST':
        form = ExpedienteForm(request.POST)
        if form.is_valid():
            expediente = form.save(commit=False)
            expediente.paciente = paciente  # Asignar automáticamente el paciente
            expediente.save()
            return redirect('expediente_paciente', paciente_id=paciente.id)
    else:
        form = ExpedienteForm(initial={'paciente': paciente})
    
    context = {
        'paciente': paciente,
        'expedientes': expedientes,
        'form': form,
    }
    
    return render(request, 'expediente_paciente.html', context)



#ELIMINAR TRATAMIENTO ASIGNADO A PACIENTE

def eliminar_expediente(request, expediente_id):
    expediente = get_object_or_404(PacienteTratamiento, id=expediente_id)
    paciente_id = expediente.paciente.id
    
    if request.method == 'POST':
        expediente.delete()
        return redirect('expediente_paciente', paciente_id=paciente_id)
    
    # Si es GET, eliminar directamente (sin confirmación)
    expediente.delete()
    return redirect('expediente_paciente', paciente_id=paciente_id)
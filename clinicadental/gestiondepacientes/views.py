from django.shortcuts import render, redirect, get_object_or_404
from .forms import PacienteForm
from django.contrib.auth.decorators import login_required
from . models import Paciente

from .models import Paciente, PacienteTratamiento
from .forms import ExpedienteForm
from citas.models import Cita

# CRUD Pacientes

@login_required
def lista(request):
    pacientes = Paciente.objects.all().order_by('apellido', 'nombre')
    return render(request, "listaPacientes.html", {"pacientes": pacientes})

# Crear paciente
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

# Editar paciente
@login_required
def edicionPaciente(request, id):
  paciente = Paciente.objects.get(id=id)
  return render(request, "edicionPaciente.html", {"paciente": paciente})

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


# Eliminar paciente
@login_required
def eliminar_paciente(request, id):
    paciente = get_object_or_404(Paciente, pk=id)
    paciente.delete()
    return redirect('lista')


# Expediente de paciente
def expediente_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    expedientes = PacienteTratamiento.objects.filter(
        paciente=paciente
    ).select_related('tratamiento', 'especialista')
    
    if request.method == 'POST':
        form = ExpedienteForm(request.POST)
        if form.is_valid():
            expediente = form.save(commit=False)
            expediente.paciente = paciente
            expediente.save()
            return redirect('expediente_paciente', paciente_id=paciente.id)
    else:
        form = ExpedienteForm(initial={'paciente': paciente})
    
    historial_citas = Cita.objects.filter(
        paciente=paciente
    ).select_related('especialista', 'tratamiento').order_by('-fecha_hora')

    context = {
        'paciente': paciente,
        'expedientes': expedientes,
        'form': form,
        'historial_citas': historial_citas
    }
    
    return render(request, 'expediente_paciente.html', context)


# Eliminar tratamiento asignado a paciente
def eliminar_expediente(request, expediente_id):
    expediente = get_object_or_404(PacienteTratamiento, id=expediente_id)
    paciente_id = expediente.paciente.id
    
    if request.method == 'POST':
        expediente.delete()
        return redirect('expediente_paciente', paciente_id=paciente_id)
    
    expediente.delete()
    return redirect('expediente_paciente', paciente_id=paciente_id)
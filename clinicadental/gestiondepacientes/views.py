from django.shortcuts import render, redirect, get_object_or_404
from .forms import CrearPacienteForm
from django.contrib.auth.decorators import login_required

from . models import Paciente

# Create your views here.


@login_required
def crudpacientes(request):
    return render(request, 'gestionpacientes.html')


'''@login_required
def crearpacientes(request):
    return render(request, 'crearpacientes.html')'''


@login_required
def crearpacientessss(request):
    if request.method == 'GET':
        return render(request, 'crearpacientes.html', {
            'form': CrearPacienteForm
        })
    else:
        try:
            form = CrearPacienteForm(request.POST)
            form.save()
            return redirect(crudpacientes)
        except:
            return render(request, 'crearpacientes.html', {
                'form': CrearPacienteForm,
                'error': 'Ingresa datos validos'
            })


@login_required
def lista(request):
    pacientes = Paciente.objects.all()
    return render(request, "listaPacientes.html", {"pacientes": pacientes})

#@login_required
#def edicionPaciente(request, id):
#   paciente = Paciente.objects.get(id=id)
#    return render(request, "edicionPaciente.html", {"paciente": paciente})

@login_required
def editarPaciente(request):
    
    paciente_id= request.POST['id']
    nombre = request.POST['nombre']
    apellido = request.POST['apellido']
    dui = request.POST['dui']
    fecha_ingreso = request.POST['fecha_ingreso']
    correo = request.POST['correo']
    telefono = request.POST['telefono']

    paciente = Paciente.objects.get(id=paciente_id)
    paciente.nombre = nombre
    paciente.apellido = apellido
    paciente.dui = dui
    paciente.fecha_ingreso = fecha_ingreso
    paciente.correo = correo
    paciente.telefono = telefono

    paciente.save()
    return redirect('lista')



@login_required
def eliminarpaciente(request, id):
    paciente = Paciente.objects.get(id=id)
    paciente.delete()

    return redirect('lista')

@login_required
def edicionPaciente(request, id):
    paciente = get_object_or_404(Paciente, id=id)

    if request.method == "POST":
        form = CrearPacienteForm(request.POST, instance=paciente, use_required_attribute=False)
        if form.is_valid():
            form.save()
            return redirect(lista)
    else:
        form = CrearPacienteForm(instance=paciente, use_required_attribute=False)

    return render(request, "edicionPaciente.html", {"form": form})

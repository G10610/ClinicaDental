from django.shortcuts import render, redirect
from .forms import CrearPacienteForm
from django.contrib.auth.decorators import login_required

from . models import Paciente

# Create your views here.

@login_required
def crudpacientes(request):
    return render(request, 'gestionpacientes.html')
@login_required
def crearpacientes(request):
    return render(request, 'crearpacientes.html')

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
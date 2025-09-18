from django.shortcuts import render, redirect, get_object_or_404
from .forms import CrearEspecialistaForm
from django.contrib.auth.decorators import login_required

from . models import Especialista
# Create your views here.


@login_required
def crudespecialistas(request):
    return render(request, 'gestione.html')


# @login_required
# def crudespecialistas(request):
#     return render(request, 'gestiones.html')


@login_required
def crearespecialistas(request):
    if request.method == 'GET':
        return render(request, 'crearespecialistas.html', {
            'form': CrearEspecialistaForm
        })
    else:
        try:
            form = CrearEspecialistaForm(request.POST)
            form.save()
            return redirect(crudespecialistas)
        except:
            return render(request, 'crearespecialistas.html', {
                'form': CrearEspecialistaForm,
                'error': 'Ingresa datos validos'
            })


@login_required
def listaespecialistas(request):
    especialistas = Especialista.objects.all()
    return render(request, "listaespecialistas.html", {"especialistas": especialistas})


# @login_required
# def edicionespecialista(request, id):
 #   especialista = especialista.objects.get(id=id)
 #   return render(request, "edicionespecialista.html", {"especialista": especialista})


@login_required
def editarespecialista(request):

    especialista_id = request.POST['id']
    nombre = request.POST['nombre']
    apellido = request.POST['apellido']
    dui = request.POST['dui']
    telefono = request.POST['telefono']

    especialista = Especialista.objects.get(id=id)
    especialista.nombre = nombre
    especialista.apellido = apellido
    especialista.dui = dui
    especialista.telefono = telefono

    especialista.save()
    return redirect('listaespecialistas')


@login_required
def eliminarespecialista(request, id):
    especialista = Especialista.objects.get(id=id)
    especialista.delete()

    return redirect('listaespecialistas')


@login_required
def edicionespecialista(request, id):
    especialista = get_object_or_404(Especialista, id=id)

    if request.method == "POST":
        form = CrearEspecialistaForm(
            request.POST, instance=especialista, use_required_attribute=False)
        if form.is_valid():
            form.save()
            return redirect('listaespecialistas')
    else:
        form = CrearEspecialistaForm(
            instance=especialista, use_required_attribute=False)

    return render(request, "edicionespecialista.html", {"form": form})

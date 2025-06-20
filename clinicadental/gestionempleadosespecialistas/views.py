from django.shortcuts import render, redirect
from .forms import CrearEmpleadoForm


# Create your views here.


def crudempleados(request):
    return render(request, 'gestione.html')


def crudespecialistas(request):
    return render(request, 'gestiones.html')


def crearempleados(request):
    if request.method == 'GET':
        return render(request, 'crearempleados.html', {
            'form': CrearEmpleadoForm
        })
    else:
        try:
            form = CrearEmpleadoForm(request.POST)
            form.save()
            return redirect(crudempleados)
        except:
            return render(request, 'crearempleados.html', {
                'form': CrearEmpleadoForm,
                'error': 'Ingresa datos validos'
            })

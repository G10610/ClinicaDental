from django.shortcuts import render, redirect
from .forms import CrearEmpleadoForm
from django.contrib.auth.decorators import login_required


# Create your views here.

@login_required
def crudempleados(request):
    return render(request, 'gestione.html')

@login_required
def crudespecialistas(request):
    return render(request, 'gestiones.html')

@login_required
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

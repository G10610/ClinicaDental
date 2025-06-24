from django.shortcuts import render, redirect, get_object_or_404
from .forms import CrearEmpleadoForm
from django.contrib.auth.decorators import login_required

from . models import Empleado
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


@login_required
def listaempleados(request):
    empleados = Empleado.objects.all()
    return render(request, "listaEmpleados.html", {"empleados": empleados})


#@login_required
#def edicionEmpleado(request, id):
 #   empleado = Empleado.objects.get(id=id)
 #   return render(request, "edicionEmpleado.html", {"empleado": empleado})


@login_required
def editarEmpleado(request):

    empleado_id = request.POST['id']
    nombre = request.POST['nombre']
    apellido = request.POST['apellido']
    dui = request.POST['dui']
    fecha_ingreso = request.POST['fecha_ingreso']
    salario = request.POST['salario']
    telefono = request.POST['telefono']

    empleado = Empleado.objects.get(id=empleado_id)
    empleado.nombre = nombre
    empleado.apellido = apellido
    empleado.dui = dui
    empleado.fecha_ingreso = fecha_ingreso
    empleado.salario = salario
    empleado.telefono = telefono

    empleado.save()
    return redirect('listaempleados')


@login_required
def eliminarEmpleado(request, id):
    empleado = Empleado.objects.get(id=id)
    empleado.delete()

    return redirect('listaempleados')

@login_required
def edicionEmpleado(request, id):
    empleado = get_object_or_404(Empleado, id=id)

    if request.method == "POST":
        form = CrearEmpleadoForm(request.POST, instance=empleado, use_required_attribute=False)
        if form.is_valid():
            form.save()
            return redirect('listaempleados')
    else:
        form = CrearEmpleadoForm(instance=empleado, use_required_attribute=False)

    return render(request, "edicionEmpleado.html", {"form": form})

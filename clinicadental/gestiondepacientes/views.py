from django.shortcuts import render

# Create your views here.


def crudpacientes(request):
    return render(request, 'gestionpacientes.html')

def crearpacientes(request):
    return render(request, 'crearpacientes.html')

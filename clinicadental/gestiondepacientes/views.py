from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def crudpacientes(request):
    return render(request, 'gestionpacientes.html')
@login_required
def crearpacientes(request):
    return render(request, 'crearpacientes.html')

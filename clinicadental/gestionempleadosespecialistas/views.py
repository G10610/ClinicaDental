from django.shortcuts import render


# Create your views here.


def crudempleados(request):
    return render(request, 'gestione.html')

def crudespecialistas(request):
    return render(request, 'gestiones.html')
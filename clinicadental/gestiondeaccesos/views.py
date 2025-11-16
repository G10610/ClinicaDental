from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError

User = get_user_model()

def signup(request):
    if request.method == 'GET':
        form = UserCreationForm()
        return render(request, 'signup.html', {'form': form})
    
    form = UserCreationForm(request.POST)
    if form.is_valid():
        try:
            user = form.save()
            login(request, user)
            return redirect('agenda')
        except IntegrityError:
            return render(request, 'signup.html', {
                'form': form,
                'error': 'El usuario ya existe'
            })
    else:
        return render(request, 'signup.html', {
            'form': form,
            'error': 'Por favor corrige los errores del formulario'
        })

@login_required
def index(request):
    return render(request, 'index.html')

@login_required
def cerrarsesion(request):
    logout(request)
    return redirect(iniciarsesion)

def iniciarsesion(request):
    if request.method == 'GET':
        form = AuthenticationForm()
        return render(request, 'iniciar.html', {'form': form})

    form = AuthenticationForm(data=request.POST)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('agenda')
    else:
        return render(request, 'iniciar.html', {
            'form': form,
            'error': 'Usuario o contraseña incorrecta'
        })

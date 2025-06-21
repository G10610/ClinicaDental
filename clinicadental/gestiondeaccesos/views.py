from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Create your views here.


def home(request):
    return render(request, 'home.html')

def signup(request):

    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        }
        )
    else:
        if request.POST['password1'] == request.POST['password2']:
            # registrar usuario
            try:
                user = User.objects.create_user(username=request.POST['username'],
                                                password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect(home)
            except:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    "error": 'El Usuario ya Existe'
                }
                )
        return render(request, 'signup.html', {
            'form': UserCreationForm,
            "error": 'Contraseñas no coinciden'
        }
        )

@login_required
def index(request):
    return render(request, 'index.html')

@login_required
def cerrarsesion(request):
    logout(request)
    return redirect(home)


def iniciarsesion(request):
    if request.method == 'GET':
        return render(request, 'iniciar.html', {
            'form': AuthenticationForm
        }
        )
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'iniciar.html',{
                'form': AuthenticationForm,
                'error': 'Usuario o Contraseña Incorrecta'
            })
        else:
            login(request, user)
            return redirect(home)

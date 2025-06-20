from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('index/', views.index, name='index'),
    path('registrarse/', views.signup, name='signup'),
    path('iniciarsesion/', views.iniciarsesion, name='login'),
    path('salir/', views.cerrarsesion, name='logout'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.crudpacientes, name='crudpacientes'),
    path('crearpa/', views.crearpacientessss, name='crearpacientes'),
    path('lista/', views.lista, name='lista'),
    
]
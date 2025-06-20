from django.urls import path
from . import views

urlpatterns = [
    path('', views.crudpacientes, name='crudpacientes'),
    path('crearpa/', views.crearpacientes, name='crearpacientes'),
    
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.crudpacientes, name='crudpacientes'),
    path('crearpa/', views.crearpacientessss, name='crearpacientes'),
    path('lista/', views.lista, name='lista'),
    
    
    path('edicionpa/<int:id>', views.edicionPaciente, name='edicionpaciente'),
    path('editarpa/', views.editarPaciente, name='editarpaciente'),
    path('eliminarpa/<int:id>/', views.eliminarpaciente, name='eliminarpaciente'),

]

from django.urls import path
from . import views


urlpatterns = [
    path('', views.crudpacientes, name='crudpacientes'),
    path('lista/', views.lista, name='lista'),
    
    # crud

    path('crear/', views.crear_paciente, name='crearpacientes'),
    
    # Muestra el formulario de edición con los datos del paciente (GET)
    # Se usa cuando se hace clic en el botón "Editar" desde la lista de pacientes.
    path('edicionpaciente/<int:id>', views.edicionPaciente, name='edicionpaciente'),

    # Procesa los datos modificados y guarda los cambios (POST)
    # Es la acción del formulario dentro de la página de edición.
    path('editarpaciente/', views.editarPaciente, name='editarpaciente'), 


    path('eliminar/<int:id>/', views.eliminar_paciente, name='eliminarpaciente'),
]

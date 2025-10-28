from django.urls import path
from . import views


urlpatterns = [

    #URL de la vista de lista de tratamientos
    path('lista_tratamientos/', views.lista_tratamientos, name='lista_tratamientosss'),

    #URL de la creacion de tratamientos
    path('crear_tratamiento/', views.crear_tratamiento, name='crear_tratamiento'),


    # Muestra el formulario de edición con los datos del paciente (GET)
    # Se usa cuando se hace clic en el botón "Editar" desde la lista de pacientes.
    path('ediciontratamiento/<int:id>', views.edicionTratamiento, name='ediciontratamiento'),

    # Procesa los datos modificados y guarda los cambios (POST)
    # Es la acción del formulario dentro de la página de edición.
    path('editartratamiento/', views.editarTratamiento, name='editartratamiento'), 

    #URL que activa la eliminacion de un tratamiento
    path('eliminar/<int:id>/', views.eliminar_tratamiento, name='eliminartratamiento'),

    ]
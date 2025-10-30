from django.urls import path
from . import views

urlpatterns = [

    # copia
    

    path('listae/', views.listae, name='listae'),
    path('creare/', views.crear_especialista, name='crearespecialista'),
    path('edicionespecialista/<int:id>', views.edicionEspecialista, name='edicionespecialista'),
    
    # Procesa los datos modificados y guarda los cambios (POST)
    # Es la acción del formulario dentro de la página de edición.
    path('editarespecialista/', views.editarEspecialista, name='editarespecialista'),
    
    path('eliminar/<int:id>/', views.eliminar_especialista, name='eliminarespecialista'),
  
]

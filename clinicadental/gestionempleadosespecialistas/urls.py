from django.urls import path
from . import views

urlpatterns = [
    path('empleados/', views.crudempleados, name='crudempleados'),
    path('especialistas/', views.crudespecialistas, name='crudespecialistas'),
    path('crearempleados/', views.crearempleados, name='crearempleados'),
    path('listaempleados/', views.listaempleados, name='listaempleados'),
    
    path('edicionempleado/<int:id>', views.edicionEmpleado, name='edicionempleado'),
    
    path('editarempleado/', views.editarEmpleado, name='editarempleado'),
    
    path('eliminarempleado/<int:id>/', views.eliminarEmpleado, name='eliminarempleado'),
]

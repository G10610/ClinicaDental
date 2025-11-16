from django.urls import path
from . import views

urlpatterns = [
    path('', views.agenda, name='agenda'),
    path('agenda/semanal/', views.agenda_semanal, name='agenda_semanal'),
    path('citas/crear/', views.crear_cita, name='crear_cita'),
    path('buscar_pacientes/', views.buscar_pacientes, name='buscar_pacientes'),
    path('api/get-citas/', views.api_get_citas, name='api_get_citas'),
    path('api/get-citas_semana/', views.api_get_citas_semana, name='api_get_citas_semana'),
    path('citas/api/cambiar-estado/', views.api_cambiar_estado, name='api_cambiar_estado'),
    path('citas/editar/<int:cita_id>/', views.editar_cita, name='editar_cita'),
]
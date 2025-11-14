from django.urls import path
from . import views

urlpatterns = [
    path('', views.gestionar_configuracion, name='gestionar_configuracion'),
]
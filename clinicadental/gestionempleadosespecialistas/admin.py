from django.contrib import admin
from .models import Empleado # Importamos los modelos del archivo .model de la app

# Register your models here.

admin.site.register(Empleado)
from django.contrib import admin
# Importamos los modelos del archivo .model de la app
from .models import Especialista

# Register your models here.

admin.site.register(Especialista)

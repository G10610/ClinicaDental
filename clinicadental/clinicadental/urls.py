"""
URL configuration for clinicadental project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
# from gestiondeaccesos import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('gestiondeaccesos.urls')),
    path('gestionpacientes/', include('gestiondepacientes.urls')),
    path('gestionee/', include('gestionespecialistas.urls')),
    path('gestiontratamientos/', include('gestiontratamientos.urls')),
    path('', include('citas.urls')),  
    path('configuracion/', include('configuracion.urls')),
    path('citas/', include('citas.urls')),

]

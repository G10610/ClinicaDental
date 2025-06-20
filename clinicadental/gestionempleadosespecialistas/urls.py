from django.urls import path
from . import views

urlpatterns = [
    path('empleados/', views.crudempleados, name='crudempleados'),
    path('especialistas/', views.crudespecialistas, name='crudespecialistas'),
    path('crearempleados/', views.crearempleados, name='crearempleados'),
]
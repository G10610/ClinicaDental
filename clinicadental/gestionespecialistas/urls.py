from django.urls import path
from . import views

urlpatterns = [
    path('especialistas/', views.crudespecialistas, name='crudespecialistas'),
    path('crearespecialistas/', views.crearespecialistas,
         name='crearespecialistas'),
    path('listaespecialistas/', views.listaespecialistas,
         name='listaespecialistas'),

    path('edicionespecialista/<int:id>',
         views.edicionespecialista, name='edicionespecialista'),

    path('editarespecialista/', views.editarespecialista,
         name='editarespecialista'),

    path('eliminarespecialista/<int:id>/',
         views.eliminarespecialista, name='eliminarespecialista'),
]

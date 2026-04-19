from django.urls import path
from . import views

app_name = 'grades'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Careers
    path('carreras/', views.career_list, name='career_list'),
    path('carreras/nueva/', views.career_create, name='career_create'),
    path('carreras/<int:pk>/editar/', views.career_update, name='career_update'),
    path('carreras/<int:pk>/eliminar/', views.career_delete, name='career_delete'),

    # Semesters
    path('carreras/<int:career_pk>/semestres/', views.semester_list, name='semester_list'),
    path('carreras/<int:career_pk>/semestres/nuevo/', views.semester_create, name='semester_create'),
    path('semestres/<int:pk>/editar/', views.semester_update, name='semester_update'),
    path('semestres/<int:pk>/eliminar/', views.semester_delete, name='semester_delete'),

    # Subjects
    path('semestres/<int:semester_pk>/materias/', views.subject_list, name='subject_list'),
    path('semestres/<int:semester_pk>/materias/nueva/', views.subject_create, name='subject_create'),
    path('materias/<int:pk>/', views.subject_detail, name='subject_detail'),
    path('materias/<int:pk>/editar/', views.subject_update, name='subject_update'),
    path('materias/<int:pk>/eliminar/', views.subject_delete, name='subject_delete'),
]

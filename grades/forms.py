from django import forms
from .models import Career, Semester, Subject


class CareerForm(forms.ModelForm):
    class Meta:
        model = Career
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Ingeniería en Sistemas',
                'autofocus': True,
            })
        }
        labels = {'name': 'Nombre de la carrera'}


class SemesterForm(forms.ModelForm):
    class Meta:
        model = Semester
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Semestre 1, Semestre 2024-1',
                'autofocus': True,
            })
        }
        labels = {'name': 'Nombre del semestre'}


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'desired_grade']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Cálculo Diferencial',
                'autofocus': True,
            }),
            'desired_grade': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '7.00',
                'step': '0.01',
                'min': '0',
                'max': '10',
            }),
        }
        labels = {
            'name': 'Nombre de la materia',
            'desired_grade': 'Nota deseada (0–10)',
        }


class GradeUpdateForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['progress1', 'progress2', 'progress3']
        widgets = {
            'progress1': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg text-center',
                'placeholder': '—',
                'step': '0.01',
                'min': '0',
                'max': '10',
            }),
            'progress2': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg text-center',
                'placeholder': '—',
                'step': '0.01',
                'min': '0',
                'max': '10',
            }),
            'progress3': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg text-center',
                'placeholder': '—',
                'step': '0.01',
                'min': '0',
                'max': '10',
            }),
        }
        labels = {
            'progress1': 'Primer progreso',
            'progress2': 'Segundo progreso',
            'progress3': 'Tercer progreso',
        }

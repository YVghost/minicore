from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Career(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='careers')
    name = models.CharField(max_length=200, verbose_name='Nombre de la carrera')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Carrera'
        verbose_name_plural = 'Carreras'

    def __str__(self):
        return self.name

    def get_overall_average(self):
        subjects = Subject.objects.filter(semester__career=self)
        finished = [s for s in subjects if s.final_grade is not None]
        if not finished:
            return None
        return round(sum(s.final_grade for s in finished) / len(finished), 2)


class Semester(models.Model):
    career = models.ForeignKey(Career, on_delete=models.CASCADE, related_name='semesters')
    name = models.CharField(max_length=100, verbose_name='Nombre del semestre')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Semestre'
        verbose_name_plural = 'Semestres'

    def __str__(self):
        return f"{self.career.name} — {self.name}"

    def get_average(self):
        subjects = self.subjects.all()
        finished = [s for s in subjects if s.final_grade is not None]
        if not finished:
            return None
        return round(sum(s.final_grade for s in finished) / len(finished), 2)

    def get_status(self):
        subjects = list(self.subjects.all())
        if not subjects:
            return 'empty'
        finished = [s for s in subjects if s.final_grade is not None]
        if len(finished) == len(subjects):
            return 'complete'
        if finished:
            return 'in_progress'
        return 'not_started'


_grade_validators = [MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('10'))]


class Subject(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=200, verbose_name='Nombre de la materia')
    desired_grade = models.DecimalField(
        max_digits=4, decimal_places=2,
        validators=_grade_validators,
        verbose_name='Nota deseada',
        help_text='Nota que deseas obtener (0–10)'
    )
    progress1 = models.DecimalField(
        max_digits=4, decimal_places=2,
        validators=_grade_validators,
        null=True, blank=True,
        verbose_name='Primer progreso (25%)'
    )
    progress2 = models.DecimalField(
        max_digits=4, decimal_places=2,
        validators=_grade_validators,
        null=True, blank=True,
        verbose_name='Segundo progreso (35%)'
    )
    progress3 = models.DecimalField(
        max_digits=4, decimal_places=2,
        validators=_grade_validators,
        null=True, blank=True,
        verbose_name='Tercer progreso (40%)'
    )

    WEIGHT_P1 = Decimal('0.25')
    WEIGHT_P2 = Decimal('0.35')
    WEIGHT_P3 = Decimal('0.40')
    PASSING_GRADE = Decimal('7.00')

    class Meta:
        ordering = ['name']
        verbose_name = 'Materia'
        verbose_name_plural = 'Materias'

    def __str__(self):
        return self.name

    @property
    def current_grade(self):
        total = Decimal('0')
        if self.progress1 is not None:
            total += self.progress1 * self.WEIGHT_P1
        if self.progress2 is not None:
            total += self.progress2 * self.WEIGHT_P2
        if self.progress3 is not None:
            total += self.progress3 * self.WEIGHT_P3
        return round(total, 2)

    @property
    def final_grade(self):
        if all(p is not None for p in [self.progress1, self.progress2, self.progress3]):
            return self.current_grade
        return None

    @property
    def is_passing(self):
        fg = self.final_grade
        if fg is not None:
            return fg >= self.PASSING_GRADE
        return None

    @property
    def progresses_entered(self):
        return sum(1 for p in [self.progress1, self.progress2, self.progress3] if p is not None)

    @property
    def prediction(self):
        desired = self.desired_grade
        p1 = self.progress1
        p2 = self.progress2
        p3 = self.progress3

        if p1 is not None and p2 is not None and p3 is not None:
            final = self.current_grade
            return {
                'status': 'complete',
                'final_grade': final,
                'achieved': final >= desired,
                'message': f'Nota final: {final}',
            }

        if p1 is not None and p2 is not None:
            current = p1 * self.WEIGHT_P1 + p2 * self.WEIGHT_P2
            needed = (desired - current) / self.WEIGHT_P3
            needed = round(needed, 2)
            achievable = Decimal('0') <= needed <= Decimal('10')
            return {
                'status': 'need_p3',
                'current': round(current, 2),
                'needed': needed,
                'achievable': achievable,
                'message': f'Necesitas {needed} en el tercer progreso',
            }

        if p1 is not None:
            current = p1 * self.WEIGHT_P1
            remaining_weight = self.WEIGHT_P2 + self.WEIGHT_P3
            needed = (desired - current) / remaining_weight
            needed = round(needed, 2)
            achievable = Decimal('0') <= needed <= Decimal('10')
            return {
                'status': 'need_p2_p3',
                'current': round(current, 2),
                'needed': needed,
                'achievable': achievable,
                'message': f'Necesitas un promedio de {needed} en 2do y 3er progreso',
            }

        return {
            'status': 'no_data',
            'message': 'Ingresa tus notas para ver la predicción',
        }

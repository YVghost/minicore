from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Career, Semester, Subject
from .forms import CareerForm, SemesterForm, SubjectForm, GradeUpdateForm


# ─── Dashboard ───────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    careers = Career.objects.filter(user=request.user).prefetch_related('semesters__subjects')
    total_subjects = Subject.objects.filter(semester__career__user=request.user).count()
    total_passing = sum(
        1 for s in Subject.objects.filter(semester__career__user=request.user)
        if s.is_passing is True
    )
    total_failing = sum(
        1 for s in Subject.objects.filter(semester__career__user=request.user)
        if s.is_passing is False
    )
    context = {
        'careers': careers,
        'total_subjects': total_subjects,
        'total_passing': total_passing,
        'total_failing': total_failing,
    }
    return render(request, 'grades/dashboard.html', context)


# ─── Career ──────────────────────────────────────────────────────────────────

@login_required
def career_list(request):
    careers = Career.objects.filter(user=request.user)
    return render(request, 'grades/career_list.html', {'careers': careers})


@login_required
def career_create(request):
    if request.method == 'POST':
        form = CareerForm(request.POST)
        if form.is_valid():
            career = form.save(commit=False)
            career.user = request.user
            career.save()
            messages.success(request, f'Carrera "{career.name}" creada correctamente.')
            return redirect('grades:semester_list', career_pk=career.pk)
    else:
        form = CareerForm()
    return render(request, 'grades/career_form.html', {'form': form, 'action': 'Crear'})


@login_required
def career_update(request, pk):
    career = get_object_or_404(Career, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CareerForm(request.POST, instance=career)
        if form.is_valid():
            form.save()
            messages.success(request, f'Carrera actualizada correctamente.')
            return redirect('grades:career_list')
    else:
        form = CareerForm(instance=career)
    return render(request, 'grades/career_form.html', {
        'form': form, 'career': career, 'action': 'Editar'
    })


@login_required
def career_delete(request, pk):
    career = get_object_or_404(Career, pk=pk, user=request.user)
    if request.method == 'POST':
        name = career.name
        career.delete()
        messages.success(request, f'Carrera "{name}" eliminada.')
        return redirect('grades:career_list')
    return render(request, 'grades/career_confirm_delete.html', {'career': career})


# ─── Semester ─────────────────────────────────────────────────────────────────

@login_required
def semester_list(request, career_pk):
    career = get_object_or_404(Career, pk=career_pk, user=request.user)
    semesters = career.semesters.prefetch_related('subjects')
    return render(request, 'grades/semester_list.html', {
        'career': career, 'semesters': semesters
    })


@login_required
def semester_create(request, career_pk):
    career = get_object_or_404(Career, pk=career_pk, user=request.user)
    if request.method == 'POST':
        form = SemesterForm(request.POST)
        if form.is_valid():
            semester = form.save(commit=False)
            semester.career = career
            semester.save()
            messages.success(request, f'Semestre "{semester.name}" creado correctamente.')
            return redirect('grades:semester_list', career_pk=career.pk)
    else:
        form = SemesterForm()
    return render(request, 'grades/semester_form.html', {
        'form': form, 'career': career, 'action': 'Crear'
    })


@login_required
def semester_update(request, pk):
    semester = get_object_or_404(Semester, pk=pk, career__user=request.user)
    if request.method == 'POST':
        form = SemesterForm(request.POST, instance=semester)
        if form.is_valid():
            form.save()
            messages.success(request, 'Semestre actualizado correctamente.')
            return redirect('grades:semester_list', career_pk=semester.career.pk)
    else:
        form = SemesterForm(instance=semester)
    return render(request, 'grades/semester_form.html', {
        'form': form, 'semester': semester, 'career': semester.career, 'action': 'Editar'
    })


@login_required
def semester_delete(request, pk):
    semester = get_object_or_404(Semester, pk=pk, career__user=request.user)
    if request.method == 'POST':
        career_pk = semester.career.pk
        name = semester.name
        semester.delete()
        messages.success(request, f'Semestre "{name}" eliminado.')
        return redirect('grades:semester_list', career_pk=career_pk)
    return render(request, 'grades/semester_confirm_delete.html', {'semester': semester})


# ─── Subject ──────────────────────────────────────────────────────────────────

@login_required
def subject_list(request, semester_pk):
    semester = get_object_or_404(Semester, pk=semester_pk, career__user=request.user)
    subjects = semester.subjects.all()
    return render(request, 'grades/subject_list.html', {
        'semester': semester, 'subjects': subjects
    })


@login_required
def subject_create(request, semester_pk):
    semester = get_object_or_404(Semester, pk=semester_pk, career__user=request.user)
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.semester = semester
            subject.save()
            messages.success(request, f'Materia "{subject.name}" añadida correctamente.')
            return redirect('grades:subject_list', semester_pk=semester.pk)
    else:
        form = SubjectForm()
    return render(request, 'grades/subject_form.html', {
        'form': form, 'semester': semester, 'action': 'Añadir'
    })


@login_required
def subject_update(request, pk):
    subject = get_object_or_404(Subject, pk=pk, semester__career__user=request.user)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Materia actualizada correctamente.')
            return redirect('grades:subject_detail', pk=subject.pk)
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'grades/subject_form.html', {
        'form': form, 'subject': subject,
        'semester': subject.semester, 'action': 'Editar'
    })


@login_required
def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk, semester__career__user=request.user)
    if request.method == 'POST':
        semester_pk = subject.semester.pk
        name = subject.name
        subject.delete()
        messages.success(request, f'Materia "{name}" eliminada.')
        return redirect('grades:subject_list', semester_pk=semester_pk)
    return render(request, 'grades/subject_confirm_delete.html', {'subject': subject})


@login_required
def subject_detail(request, pk):
    subject = get_object_or_404(Subject, pk=pk, semester__career__user=request.user)

    if request.method == 'POST':
        form = GradeUpdateForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notas guardadas correctamente.')
            return redirect('grades:subject_detail', pk=pk)
        else:
            messages.error(request, 'Por favor revisa los valores ingresados.')
    else:
        form = GradeUpdateForm(instance=subject)

    prediction = subject.prediction
    context = {
        'subject': subject,
        'form': form,
        'prediction': prediction,
        'semester': subject.semester,
        'career': subject.semester.career,
    }
    return render(request, 'grades/subject_detail.html', context)

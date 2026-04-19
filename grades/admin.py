from django.contrib import admin
from .models import Career, Semester, Subject


class SemesterInline(admin.TabularInline):
    model = Semester
    extra = 0


class SubjectInline(admin.TabularInline):
    model = Subject
    extra = 0


@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_at']
    list_filter = ['user']
    inlines = [SemesterInline]


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ['name', 'career', 'created_at']
    list_filter = ['career__user']
    inlines = [SubjectInline]


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'semester', 'desired_grade', 'progress1', 'progress2', 'progress3']
    list_filter = ['semester__career__user']

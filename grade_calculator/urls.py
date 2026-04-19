from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('grades:dashboard'), name='home'),
    path('cuenta/', include('accounts.urls')),
    path('app/', include('grades.urls')),
]

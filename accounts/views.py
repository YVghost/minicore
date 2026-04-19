from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import RegisterForm, LoginForm


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_invalid(self, form):
        messages.error(self.request, 'Usuario o contraseña incorrectos.')
        return super().form_invalid(form)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('grades:dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Bienvenido, {user.first_name}! Tu cuenta fue creada exitosamente.')
            return redirect('grades:dashboard')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('accounts:login')

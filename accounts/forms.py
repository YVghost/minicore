from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=100, required=True, label='Nombres',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tus nombres'})
    )
    last_name = forms.CharField(
        max_length=100, required=True, label='Apellidos',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tus apellidos'})
    )
    email = forms.EmailField(
        required=True, label='Correo electrónico',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@udla.edu.ec'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
        }
        labels = {'username': 'Usuario'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-control', 'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-control', 'placeholder': 'Confirmar contraseña'
        })
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget = forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'Nombre de usuario'
        })
        self.fields['username'].label = 'Usuario'
        self.fields['password'].widget = forms.PasswordInput(attrs={
            'class': 'form-control', 'placeholder': 'Contraseña'
        })
        self.fields['password'].label = 'Contraseña'

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from libros.models import Autor, Libro, Calificación, Reseña

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este correo electrónico ya está registrado.")
        return email
    
class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = ['titulo', 'isbn', 'editorial', 'descripcion', 'imagen_portada', 'autor', 'generos']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'generos': forms.CheckboxSelectMultiple()
        }

class AutorForm(forms.ModelForm):
    class Meta:
        model = Autor
        fields = ['nombre']


class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificación
        fields = ['puntaje']
        widgets = {
            'puntaje': forms.Select(choices=[(i, f"{i} estrellas") for i in range(1, 6)], attrs={'class': 'form-select'})
        }

class ReseñaForm(forms.ModelForm):
    class Meta:
        model = Reseña
        fields = ['comentario', 'positiva']
        widgets = {
            'comentario': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'positiva': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
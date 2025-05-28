from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Autor(models.Model):
    nombre = models.CharField(max_length=100)
    nacionalidad = models.CharField(max_length=100)
    biografia = models.TextField(blank=True, null=True)
    foto = models.ImageField(upload_to='autores/', blank=True, null=True)

    def __str__(self):
        return self.nombre

class Genero(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    fecha_emision = models.DateField()
    descripcion = models.TextField()
    isbn = models.CharField(max_length=13, unique=True)
    editorial = models.CharField(max_length=100)
    idioma = models.CharField(max_length=50)
    pdf_url = models.FileField(upload_to='libros/pdf/')
    imagen_portada = models.ImageField(upload_to='libros/portadas/', blank=True, null=True)

    autor = models.ForeignKey(Autor, on_delete=models.CASCADE)
    generos = models.ManyToManyField(Genero)
    usuario_subio = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo
    

class Reseña(models.Model):
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='resenas')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    comentario = models.TextField()
    positiva = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Reseña de {self.usuario.username} en {self.libro.titulo}'

class Calificación(models.Model):
    libro = models.ForeignKey('Libro', on_delete=models.CASCADE, related_name='calificaciones')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    puntaje = models.IntegerField()  # Ej: de 1 a 5
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('libro', 'usuario')  # Un usuario no puede calificar el mismo libro dos veces

    def __str__(self):
        return f"{self.puntaje}⭐ por {self.usuario.username} a {self.libro.titulo}"
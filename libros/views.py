from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from rest_framework import filters, viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError, PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Count
from .forms import LibroForm, AutorForm
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import action
from django.shortcuts import render, get_object_or_404, redirect
from .models import Libro, Calificación, Reseña
from .forms import CalificacionForm, ReseñaForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Count

from .models import Autor, Genero, Libro, Reseña, Calificación
from .serializers import (
    AutorSerializer, GeneroSerializer, LibroSerializer,
    ReseñaSerializer, CalificaciónSerializer, RegistroUsuarioSerializer
)
from .forms import RegistroForm
from rest_framework.views import APIView

# ===================== API ViewSets =====================

class AutorViewSet(viewsets.ModelViewSet):
    queryset = Autor.objects.all()
    serializer_class = AutorSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class GeneroViewSet(viewsets.ModelViewSet):
    queryset = Genero.objects.all()
    serializer_class = GeneroSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class LibroViewSet(viewsets.ModelViewSet):
    serializer_class = LibroSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['idioma', 'autor', 'generos']
    search_fields = ['titulo', 'descripcion', 'autor__nombre']
    ordering_fields = ['fecha_emision', 'titulo']

    def get_queryset(self):
        return Libro.objects.annotate(
            promedio_calificacion=Avg('calificaciones__puntaje'),
            total_resenas=Count('resenas')
        )
    
    @action(detail=False, methods=['get'])
    def index(self, request):
        return Response({"message": "Página de inicio de libros"})

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(usuario_subio=self.request.user)

    def update(self, request, *args, **kwargs):
        libro = self.get_object()
        if libro.usuario_subio != request.user:
            raise PermissionDenied("No puedes modificar este libro.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        libro = self.get_object()
        if libro.usuario_subio != request.user:
            raise PermissionDenied("No puedes eliminar este libro.")
        return super().destroy(request, *args, **kwargs)

def index(request):
    libros = Libro.objects.all().prefetch_related('generos', 'autor')
    generos = Genero.objects.all().order_by('nombre')  # Evita duplicados, ordenado alfabéticamente
    return render(request, 'index.html', {
        'libros': libros,
        'generos': generos,
    })


@login_required
def libro_detalle(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)

    calificacion_existente = Calificación.objects.filter(libro=libro, usuario=request.user).first()
    reseña_existente = Reseña.objects.filter(libro=libro, usuario=request.user).first()

    if request.method == 'POST':
        calificacion_form = CalificacionForm(request.POST, instance=calificacion_existente)
        reseña_form = ReseñaForm(request.POST, instance=reseña_existente)

        if calificacion_form.is_valid() and reseña_form.is_valid():
            calificacion = calificacion_form.save(commit=False)
            calificacion.usuario = request.user
            calificacion.libro = libro
            calificacion.save()

            reseña = reseña_form.save(commit=False)
            reseña.usuario = request.user
            reseña.libro = libro
            reseña.save()

            return redirect('libro_detalle', libro_id=libro.id)
    else:
        calificacion_form = CalificacionForm(instance=calificacion_existente)
        reseña_form = ReseñaForm(instance=reseña_existente)

    promedio = libro.calificaciones.aggregate(prom=Avg('puntaje'))['prom']
    reseñas = libro.resenas.all().order_by('-fecha')

    # 🔹 Añadir la calificación a cada reseña
    for reseña in reseñas:
        reseña.calificacion = Calificación.objects.filter(libro=libro, usuario=reseña.usuario).first()

    return render(request, 'libros/libro_detalle.html', {
        'libro': libro,
        'promedio': promedio,
        'calificacion_form': calificacion_form,
        'reseña_form': reseña_form,
        'reseñas': reseñas,
    })


def agregar_resena(request, libro_id):
    libro = get_object_or_404(Libro, pk=libro_id)
    if request.method == 'POST':
        comentario = request.POST['comentario']
        positiva = request.POST['positiva'] == 'true'
        Reseña.objects.create(libro=libro, usuario=request.user, comentario=comentario, positiva=positiva)
    return redirect('libro_detalle', libro_id=libro_id)

def calificar_libro(request, libro_id):
    libro = get_object_or_404(Libro, pk=libro_id)
    if request.method == 'POST':
        puntaje = int(request.POST['puntaje'])
        calificacion, created = Calificación.objects.update_or_create(
            libro=libro,
            usuario=request.user,
            defaults={'puntaje': puntaje}
        )
    return redirect('libro_detalle', libro_id=libro_id)

class ReseñaViewSet(viewsets.ModelViewSet):
    queryset = Reseña.objects.all()
    serializer_class = ReseñaSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(usuario_subio=self.request.user)


class CalificaciónViewSet(viewsets.ModelViewSet):
    serializer_class = CalificaciónSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Calificación.objects.filter(usuario=self.request.user)
        return Calificación.objects.none()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        usuario = self.request.user
        libro = serializer.validated_data['libro']
        if Calificación.objects.filter(libro=libro, usuario=usuario).exists():
            raise ValidationError("Ya calificaste este libro.")
        serializer.save(usuario=usuario)

    def update(self, request, *args, **kwargs):
        calificacion = self.get_object()
        if calificacion.usuario != request.user:
            raise PermissionDenied("No puedes modificar esta calificación.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        calificacion = self.get_object()
        if calificacion.usuario != request.user:
            raise PermissionDenied("No puedes eliminar esta calificación.")
        return super().destroy(request, *args, **kwargs)


# ===================== Registro de Usuario (HTML con validación) =====================


def registro_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # Validación simple de contraseñas
        if password1 != password2:
            return render(request, "resgistration/registro.html", {"error": "Las contraseñas no coinciden."})

        if User.objects.filter(username=username).exists():
            return render(request, "registration/registro.html", {"error": "El nombre de usuario ya existe."})

        if User.objects.filter(email=email).exists():
            return render(request, "registration/registro.html", {"error": "El correo ya está en uso."})

        # Crear el usuario
        user = User.objects.create_user(username=username, email=email, password=password1)
        return render(request, "registration/registro.html", {"success": "Cuenta creada con éxito."})
    
    return render(request, "registration/registro.html")

# ===================== Login y Logout =====================

@csrf_protect
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if not request.POST.get("remember_me"):
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(60 * 60 * 24 * 7)
            return redirect("index")
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("index")


# ===================== Validación AJAX =====================

def check_usuario_correo(request):
    username = request.GET.get('username')
    email = request.GET.get('email')
    return JsonResponse({
        'username_exists': User.objects.filter(username=username).exists(),
        'email_exists': User.objects.filter(email=email).exists()
    })


@api_view(['GET'])
def verificar_existencia_usuario(request):
    username = request.query_params.get('username')
    email = request.query_params.get('email')
    return Response({
        'username_existente': User.objects.filter(username=username).exists() if username else False,
        'email_existente': User.objects.filter(email=email).exists() if email else False
    })


# ===================== Vista Index para frontend =====================

def index(request):
    query = request.GET.get('q', '')
    libros = Libro.objects.annotate(
        promedio_calificacion=Avg('calificaciones__puntaje'),
        total_resenas=Count('resenas')
    )

    if query:
        libros = libros.filter(
            Q(titulo__icontains=query) |
            Q(autor__nombre__icontains=query)
        )

    generos = Genero.objects.all()
    return render(request, 'index.html', {
        'libros': libros,
        'generos': generos,
    })

class RegistroUsuarioView(APIView):
    def post(self, request):
        serializer = RegistroUsuarioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"mensaje": "Usuario registrado correctamente."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@login_required
def registrar_libro_view(request):
    if request.method == 'POST':
        titulo = request.POST['titulo']
        descripcion = request.POST.get('descripcion', '')
        idioma = request.POST['idioma']
        fecha_emision = request.POST.get('fecha_emision')
        autor_nombre = request.POST['autor']
        nombres_generos = request.POST.getlist('generos')
        isbn = request.POST['isbn']
        editorial = request.POST['editorial']

        autor = Autor.objects.filter(nombre=autor_nombre).first()
        generos = Genero.objects.filter(nombre__in=nombres_generos)

        pdf_url = request.FILES.get('pdf_url')
        imagen_portada = request.FILES.get('imagen_portada')

        libro = Libro.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            idioma=idioma,
            fecha_emision=fecha_emision,
            autor=autor,
            pdf_url=pdf_url,
            imagen_portada=imagen_portada,
            usuario_subio=request.user,
            isbn=isbn,
            editorial=editorial,

        )

        libro.generos.set(generos)
        libro.save()
        return redirect('index')
    # Agregar para método GET
    else:
        autores = Autor.objects.all()
        generos = Genero.objects.all()
        return render(request, 'libros/registrar_libro.html', {
            'autores': autores,
            'generos': generos,
        })

@login_required
def registrar_autor_view(request):
    if request.method == 'POST':
        form = AutorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = AutorForm()
    return render(request, 'libros/registrar_autor.html', {'form': form})
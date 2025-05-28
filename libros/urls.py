from operator import index
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AutorViewSet,
    GeneroViewSet,
    LibroViewSet,
    ReseñaViewSet,
    CalificaciónViewSet,
    RegistroUsuarioView,
    agregar_resena,
    calificar_libro,
    libro_detalle,
    registro_view,
    verificar_existencia_usuario,
    index,
    registrar_libro_view, 
    registrar_autor_view
)
router = DefaultRouter()
router.register(r'autores', AutorViewSet, basename='autor')
router.register(r'generos', GeneroViewSet, basename='genero')
router.register(r'libros', LibroViewSet, basename='libro')
router.register(r'reseñas', ReseñaViewSet, basename='reseña')
router.register(r'calificaciones', CalificaciónViewSet, basename='calificacion')


urlpatterns = [
    path('', index, name='index'),
    path('api/registro/', RegistroUsuarioView.as_view(), name='registro_api'),
    path('api/verificar/', verificar_existencia_usuario, name='verificar_existencia_usuario'),
    path('registrar/libro/', registrar_libro_view, name='registrar_libro'),
    path('registrar/autor/', registrar_autor_view, name='registrar_autor'),
    path('api/libro/<int:libro_id>/', libro_detalle, name='libro_detalle'),
    path('api/libro/<int:libro_id>/resena/', agregar_resena, name='agregar_resena'),
    path('api/libro/<int:libro_id>/calificar/', calificar_libro, name='calificar_libro'),

    path('', include(router.urls)),
]

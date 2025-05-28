"""
URL configuration for biblioteca_virtual project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.contrib.auth import views as auth_views
from biblioteca_virtual import settings
from libros.views import index, login_view, logout_view, registro_view
from libros.views import LibroViewSet  
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'libros', LibroViewSet, basename='libro')

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from libros.views import LibroViewSet

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('libros.urls')),  # tus APIs y routers
    path('login/', login_view, name='login'),  # si usas auth views
    path('registro/', registro_view, name='registro'),  # si registro está en esa app
    path('logout/', logout_view, name='logout'),
    
    # Vista HTML para la raíz "/"
        path('', index, name='index'),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
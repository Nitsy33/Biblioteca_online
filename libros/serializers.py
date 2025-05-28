from rest_framework import serializers
from .models import Autor, Genero, Libro, Reseña, Calificación
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

class AutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Autor
        fields = '__all__'

class GeneroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genero
        fields = '__all__'

class LibroSerializer(serializers.ModelSerializer):
    promedio_calificacion = serializers.FloatField(read_only=True)
    total_resenas = serializers.IntegerField(read_only=True)

    class Meta:
        model = Libro
        fields = '__all__'
        read_only_fields = ['usuario_subio']
    def validate_pdf_url(self, value):
        if not value.name.endswith('.pdf'):
            raise serializers.ValidationError("El archivo debe ser un PDF.")
        return value
    def validate_imagen_portada(self, value):
        if value and not value.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            raise serializers.ValidationError("La imagen debe ser .jpg, .jpeg o .png.")
        return value

class ReseñaSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Reseña
        fields = '__all__'
        read_only_fields = ['usuario', 'fecha']

class CalificaciónSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Calificación
        fields = '__all__'
        read_only_fields = ['usuario', 'fecha']

class RegistroUsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    token = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'token')  # ← Asegurate que 'token' esté acá
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user
    
    def get_token(self, obj):
        refresh = RefreshToken.for_user(obj)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
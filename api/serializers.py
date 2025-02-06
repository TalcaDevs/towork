from rest_framework import serializers
from users.models import Solicitud, CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'email', 'foto_perfil', 'descripcion', 'telefono', 'ubicacion', 'linkedin', 'id_portafolio_web']

class SolicitudSerializer(serializers.ModelSerializer):
    usuario = CustomUserSerializer()

    class Meta:
        model = Solicitud
        fields = '__all__'

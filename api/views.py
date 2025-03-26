from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from users.models import Solicitud, CustomUser
from api.serializers import SolicitudSerializer, CustomUserSerializer
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse

class IsAdmin(permissions.BasePermission):
    """ Permiso para administradores """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'admin'

@extend_schema_view(
    list=extend_schema(
        tags=['solicitudes'],
        description='Lista todas las solicitudes'
    ),
    retrieve=extend_schema(
        tags=['solicitudes'],
        description='Obtiene el detalle de una solicitud específica'
    ),
    create=extend_schema(
        tags=['solicitudes'],
        description='Crea una nueva solicitud'
    ),
    update=extend_schema(
        tags=['solicitudes'],
        description='Actualiza una solicitud existente'
    ),
    partial_update=extend_schema(
        tags=['solicitudes'],
        description='Actualiza parcialmente una solicitud existente'
    ),
    destroy=extend_schema(
        tags=['solicitudes'],
        description='Elimina una solicitud'
    ),
    aprobar=extend_schema(
        tags=['solicitudes'],
        description='Aprueba una solicitud',
        responses={200: OpenApiResponse(description='Usuario aprobado correctamente')}
    ),
    rechazar=extend_schema(
        tags=['solicitudes'],
        description='Rechaza una solicitud',
        responses={200: OpenApiResponse(description='Usuario rechazado correctamente')}
    )
)
class SolicitudViewSet(viewsets.ModelViewSet):
    queryset = Solicitud.objects.all()
    serializer_class = SolicitudSerializer
    permission_classes = [IsAdmin]

    @action(detail=True, methods=['patch'])
    def aprobar(self, request, pk=None):
        solicitud = self.get_object()
        solicitud.estado = "aprobado"
        solicitud.save()
        return Response({"message": "Usuario aprobado correctamente"})

    @action(detail=True, methods=['patch'])
    def rechazar(self, request, pk=None):
        solicitud = self.get_object()
        solicitud.estado = "rechazado"
        solicitud.save()
        return Response({"message": "Usuario rechazado correctamente"})
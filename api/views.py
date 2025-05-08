from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from users.models import Solicitud, CustomUser, Template
from api.serializers import SolicitudSerializer, CustomUserSerializer
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse

class IsAdmin(permissions.BasePermission):
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

# Nuevos endpoints para manejar templates
@extend_schema(
    tags=['templates'],
    description='Guarda la asignación de template para un usuario',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer', 'description': 'ID del template'},
                'name': {'type': 'string', 'description': 'Nombre del template'}
            },
            'required': ['id']
        }
    },
    responses={
        200: OpenApiResponse(description='Template asignado correctamente'),
        400: OpenApiResponse(description='Error en la solicitud'),
        404: OpenApiResponse(description='Template no encontrado')
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def save_template(request):
    # Verificar si el token de acceso es válido (ya lo hace IsAuthenticated)
    user = request.user
    
    # Obtener datos del request
    template_id = request.data.get('id')
    
    if not template_id:
        return Response({"error": "ID del template es requerido"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Buscar el template por ID
    try:
        template = Template.objects.get(pk=template_id)
        # Asignar el template al usuario
        user.template = template
        user.save()
        
        return Response({"message": "Template asignado correctamente"}, status=status.HTTP_200_OK)
    except Template.DoesNotExist:
        return Response({"error": "Template no encontrado"}, status=status.HTTP_404_NOT_FOUND)

@extend_schema(
    tags=['templates'],
    description='Obtiene información del template asignado al usuario',
    responses={
        200: OpenApiResponse(
            description='Información del template',
            response={
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'description': 'ID del template'},
                    'name': {'type': 'string', 'description': 'Nombre del template'},
                    'user_email': {'type': 'string', 'description': 'Email del usuario'}
                }
            }
        ),
        404: OpenApiResponse(description='El usuario no tiene un template asignado')
    }
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_template(request):
    user = request.user
    
    if user.template:
        return Response({
            "id": user.template.id,
            "name": user.template.name,
            "user_email": user.email
        }, status=status.HTTP_200_OK)
    else:
        return Response({"message": "El usuario no tiene un template asignado"}, status=status.HTTP_404_NOT_FOUND)
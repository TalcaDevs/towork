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

@extend_schema(
    tags=['templates'],
    description='Crea un nuevo template y lo asigna al usuario autenticado o actualiza un template existente',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer', 'description': 'ID del template a crear o actualizar', 'example': 1},
                'name': {'type': 'string', 'description': 'Nombre del template', 'example': 'Portfolio Profesional'}
            },
            'required': ['id', 'name']
        }
    },
    responses={
        201: OpenApiResponse(
            description='Template creado y asignado correctamente',
        ),
        200: OpenApiResponse(
            description='Template actualizado y asignado correctamente',
        ),
        400: OpenApiResponse(
            description='Error en la solicitud',
        )
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def save_template(request):
    user = request.user
    
    template_id = request.data.get('id')
    template_name = request.data.get('name')
    
    if not template_id or not template_name:
        return Response({"error": "ID y nombre del template son requeridos"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Crear o actualizar el template
    template, created = Template.objects.update_or_create(
        pk=template_id,
        defaults={'name': template_name}
    )
    
    # Asignar el template al usuario
    user.template = template
    user.save()
    
    if created:
        return Response({
            "message": f"Template '{template_name}' creado y asignado correctamente",
            "template_id": template.id,
            "template_name": template.name
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({
            "message": f"Template '{template_name}' actualizado y asignado correctamente",
            "template_id": template.id,
            "template_name": template.name
        }, status=status.HTTP_200_OK)
    
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
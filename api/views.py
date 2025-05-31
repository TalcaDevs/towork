from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from users.models import Request, CustomUser, Template  # Cambié Solicitud a Request
from api.serializers import RequestSerializer, CustomUserSerializer  # Cambié SolicitudSerializer a RequestSerializer
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse
from django.views.decorators.http import require_http_methods  

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'  # Cambié rol a role

@extend_schema_view(
    list=extend_schema(
        tags=['requests'],  # Cambié 'solicitudes' a 'requests'
        description='List all requests'  # Traduje a inglés
    ),
    retrieve=extend_schema(
        tags=['requests'],
        description='Get details of a specific request'
    ),
    create=extend_schema(
        tags=['requests'],
        description='Create a new request'
    ),
    update=extend_schema(
        tags=['requests'],
        description='Update an existing request'
    ),
    partial_update=extend_schema(
        tags=['requests'],
        description='Partially update an existing request'
    ),
    destroy=extend_schema(
        tags=['requests'],
        description='Delete a request'
    ),
    accept=extend_schema(  # Cambié aprobar a accept
        tags=['requests'],
        description='Accept a request',
        responses={200: OpenApiResponse(description='User accepted successfully')}
    ),
    reject=extend_schema(  # Cambié rechazar a reject
        tags=['requests'],
        description='Reject a request',
        responses={200: OpenApiResponse(description='User rejected successfully')}
    )
)
class RequestViewSet(viewsets.ModelViewSet):  # Cambié SolicitudViewSet a RequestViewSet
    queryset = Request.objects.all()  # Cambié Solicitud a Request
    serializer_class = RequestSerializer  # Cambié SolicitudSerializer a RequestSerializer
    permission_classes = [IsAdmin]

    @action(detail=True, methods=['patch'])
    def accept(self, request, pk=None):  # Cambié aprobar a accept
        req_obj = self.get_object()  # Cambié solicitud a req_obj para evitar confusión con el parámetro request
        req_obj.status = "accepted"  # Cambié estado a status y aprobado a accepted
        req_obj.save()
        return Response({"message": "User accepted successfully"})

    @action(detail=True, methods=['patch'])
    def reject(self, request, pk=None):  # Cambié rechazar a reject
        req_obj = self.get_object()
        req_obj.status = "rejected"  # Cambié estado a status y rechazado a rejected
        req_obj.save()
        return Response({"message": "User rejected successfully"})

@extend_schema(
    tags=['templates'],
    description='Create a new template and assign it to the authenticated user or update an existing template',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer', 'description': 'ID of the template to create or update', 'example': 1},
                'name': {'type': 'string', 'description': 'Name of the template', 'example': 'Professional Portfolio'}
            },
            'required': ['id', 'name']
        }
    },
    responses={
        201: OpenApiResponse(
            description='Template created and assigned successfully',
        ),
        200: OpenApiResponse(
            description='Template updated and assigned successfully',
        ),
        400: OpenApiResponse(
            description='Error in the request',
        )
    }
)
@require_http_methods(["POST"])
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def save_template(request):
    user = request.user
    
    template_id = request.data.get('id')
    template_name = request.data.get('name')
    
    if not template_id or not template_name:
        return Response({"error": "Template ID and name are required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create or update the template
    template, created = Template.objects.update_or_create(
        pk=template_id,
        defaults={'name': template_name}
    )
    
    # Assign the template to the user
    user.template = template
    user.save()
    
    if created:
        return Response({
            "message": f"Template '{template_name}' created and assigned successfully",
            "template_id": template.id,
            "template_name": template.name
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({
            "message": f"Template '{template_name}' updated and assigned successfully",
            "template_id": template.id,
            "template_name": template.name
        }, status=status.HTTP_200_OK)
    
@extend_schema(
    tags=['templates'],
    description='Get information about the template assigned to the user',
    responses={
        200: OpenApiResponse(
            description='Template information',
            response={
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'description': 'Template ID'},
                    'name': {'type': 'string', 'description': 'Template name'},
                    'user_email': {'type': 'string', 'description': 'User email'}
                }
            }
        ),
        404: OpenApiResponse(description='The user does not have an assigned template')
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
        return Response({"message": "The user does not have an assigned template"}, status=status.HTTP_404_NOT_FOUND)
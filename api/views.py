from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from users.models import Request, CustomUser
from api.serializers import RequestSerializer, CustomUserSerializer
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

@extend_schema_view(
    list=extend_schema(
        tags=['requests'],
        description='Lists all requests'
    ),
    retrieve=extend_schema(
        tags=['requests'],
        description='Gets the details of a specific request'
    ),
    create=extend_schema(
        tags=['requests'],
        description='Creates a new request'
    ),
    update=extend_schema(
        tags=['requests'],
        description='Updates an existing request'
    ),
    partial_update=extend_schema(
        tags=['requests'],
        description='Partially updates an existing request'
    ),
    destroy=extend_schema(
        tags=['requests'],
        description='Deletes a request'
    ),
    approve=extend_schema(
        tags=['requests'],
        description='Approves a request',
        responses={200: OpenApiResponse(description='User approved successfully')}
    ),
    reject=extend_schema(
        tags=['requests'],
        description='Rejects a request',
        responses={200: OpenApiResponse(description='User rejected successfully')}
    )
)
class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [IsAdmin]

    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        req_obj = self.get_object()
        req_obj.status = "accepted"
        req_obj.save()
        return Response({"message": "User approved successfully"})

    @action(detail=True, methods=['patch'])
    def reject(self, request, pk=None):
        req_obj = self.get_object()
        req_obj.status = "rejected"
        req_obj.save()
        return Response({"message": "User rejected successfully"})
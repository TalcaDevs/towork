from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from users.models import Solicitud, CustomUser
from api.serializers import SolicitudSerializer, CustomUserSerializer
from django.shortcuts import get_object_or_404
from django.shortcuts import render



class IsAdmin(permissions.BasePermission):
    """ Permiso para administradores """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'admin'

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



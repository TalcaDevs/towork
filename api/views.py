from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from users.models import Solicitud, CustomUser
from api.serializers import SolicitudSerializer, CustomUserSerializer

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

def detail(request, pk):
    person = get_object_or_404(Solicitud.usuario, pk=pk)
    return render(request, 'person_detail.html', {'usuaio': usuario})

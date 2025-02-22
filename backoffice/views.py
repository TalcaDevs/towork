from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from users.models import Solicitud
from users.models import CustomUser
from users.serializers import UserSerializer, SolicitudSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from users.models import SolicitudLog

def custom_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard") 
        else:
            return render(request, "backoffice/login.html", {"error": "Credenciales inválidas"})
    
    return render(request, "backoffice/login.html")

@login_required
def dashboard(request):
    estado = request.GET.get('estado', 'pendientes')
    user_id = request.GET.get('user_id')
    solicitud = None
    if estado in ['card_detail', 'update_status'] and user_id:
        solicitud = Solicitud.objects.get(usuario__id=user_id)
    solicitudes_pendientes = Solicitud.objects.filter(estado='pendiente')
    solicitudes_aprobadas = Solicitud.objects.filter(estado='aceptada')
    solicitudes_rechazadas = Solicitud.objects.filter(estado='rechazada')

    return render(request, 'backoffice/dashboard.html', {
        'pendientes': solicitudes_pendientes,
        'aprobados': solicitudes_aprobadas,
        'rechazados': solicitudes_rechazadas,
        'solicitud': solicitud,
        'estado': estado,
    })

@login_required
def update_status(request, user_id):
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        solicitud = Solicitud.objects.get(usuario__id=user_id)
        estado_anterior = solicitud.estado
        solicitud.estado = nuevo_estado
        solicitud.save()

        # Registrar el cambio en SolicitudLog
        SolicitudLog.objects.create(
            solicitud=solicitud,
            usuario=request.user,
            estado_anterior=estado_anterior,
            nuevo_estado=nuevo_estado
        )

        return redirect('dashboard')
    else:
        solicitud = Solicitud.objects.get(usuario__id=user_id)
        return render(request, 'backoffice/update_status.html', {'solicitud': solicitud})

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def user_list(request):
    users = CustomUser.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([permissions.IsAdminUser])  # Solo administradores pueden cambiar el estado
def change_request_status(request, user_id):
    """
    Endpoint para cambiar el estado de la solicitud de un usuario (pendiente, aceptada, rechazada).
    """
    try:
        solicitud = Solicitud.objects.get(usuario__id=user_id)
        nuevo_estado = request.data.get("estado")

        if nuevo_estado not in ["pendiente", "aceptada", "rechazada"]:
            return Response({"error": "Estado inválido"}, status=status.HTTP_400_BAD_REQUEST)

        solicitud.estado = nuevo_estado
        solicitud.save()

        return Response({"message": "Estado de solicitud actualizado correctamente"}, status=status.HTTP_200_OK)

    except Solicitud.DoesNotExist:
        return Response({"error": "Solicitud no encontrada para este usuario"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def user_detail(request, user_id):
    solicitud = Solicitud.objects.get(usuario__id=user_id)
    serializer = SolicitudSerializer(solicitud)
    return render(request, 'backoffice/detail.html', {'solicitud': serializer.data})
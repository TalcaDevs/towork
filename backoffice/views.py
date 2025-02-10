from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import Solicitud
from users.models import CustomUser
from users.serializers import UserSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status

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
    solicitudes_pendientes = Solicitud.objects.filter(estado='pendiente')
    solicitudes_aprobadas = Solicitud.objects.filter(estado='aprobado')
    solicitudes_rechazadas = Solicitud.objects.filter(estado='rechazado')

    return render(request, 'backoffice/dashboard.html', {
        'pendientes': solicitudes_pendientes,
        'aprobados': solicitudes_aprobadas,
        'rechazados': solicitudes_rechazadas,
    })

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def user_list(request):
    users = CustomUser.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([permissions.IsAdminUser])  # Solo administradores pueden cambiar el estado
def change_user_status(request, user_id):
    """
    Endpoint para cambiar el estado de un usuario (pendiente, aprobado, rechazado).
    """
    try:
        usuario = CustomUser.objects.get(id=user_id)
        nuevo_estado = request.data.get("estado")

        if nuevo_estado not in ["pendiente", "aprobado", "rechazado"]:
            return Response({"error": "Estado inválido"}, status=status.HTTP_400_BAD_REQUEST)

        usuario.estado = nuevo_estado
        usuario.save()

        return Response({"message": "Estado actualizado correctamente"}, status=status.HTTP_200_OK)

    except CustomUser.DoesNotExist:
        return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)




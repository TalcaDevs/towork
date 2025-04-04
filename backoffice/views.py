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
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
        return render(request, 'backoffice/dashboard.html', {
            'estado': estado,
            'solicitud': solicitud,
        })
    
    # Obtener las solicitudes según el estado seleccionado
    if estado == 'pendientes':
        solicitudes_list = Solicitud.objects.filter(estado='pendiente').order_by('-fecha_creacion')
    elif estado == 'aprobados':
        solicitudes_list = Solicitud.objects.filter(estado='aceptada').order_by('-fecha_creacion')
    elif estado == 'rechazados':
        solicitudes_list = Solicitud.objects.filter(estado='rechazada').order_by('-fecha_creacion')
    else:
        solicitudes_list = Solicitud.objects.filter(estado='pendiente').order_by('-fecha_creacion')
    
    # Configurar la paginación
    page = request.GET.get('page', 1)
    items_per_page = 5  # Puedes ajustar este número según tus necesidades
    paginator = Paginator(solicitudes_list, items_per_page)
    
    try:
        solicitudes = paginator.page(page)
    except PageNotAnInteger:
        # Si la página no es un número, mostrar la primera página
        solicitudes = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango, mostrar la última página
        solicitudes = paginator.page(paginator.num_pages)
    
    # Obtener contadores para la sidebar
    solicitudes_pendientes_count = Solicitud.objects.filter(estado='pendiente').count()
    solicitudes_aprobadas_count = Solicitud.objects.filter(estado='aceptada').count()
    solicitudes_rechazadas_count = Solicitud.objects.filter(estado='rechazada').count()
    
    return render(request, 'backoffice/dashboard.html', {
        'pendientes': solicitudes if estado == 'pendientes' else None,
        'aprobados': solicitudes if estado == 'aprobados' else None,
        'rechazados': solicitudes if estado == 'rechazados' else None,
        'pendientes_count': solicitudes_pendientes_count,
        'aprobados_count': solicitudes_aprobadas_count,
        'rechazados_count': solicitudes_rechazadas_count,
        'estado': estado,
        'page_obj': solicitudes,
        'paginator': paginator,
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

@extend_schema(
    tags=['backoffice'],
    description='Obtiene la lista de usuarios con toda su información.',
    responses={
        200: UserSerializer(many=True)
    }
)
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def user_list(request):
    users = CustomUser.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@extend_schema(
    tags=['backoffice'],
    description='Endpoint para cambiar el estado de la solicitud de un usuario (pendiente, aceptada, rechazada).',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'estado': {'type': 'string', 'enum': ['pendiente', 'aceptada', 'rechazada']}
            },
            'required': ['estado']
        }
    },
    responses={
        200: OpenApiResponse(description='Estado de solicitud actualizado correctamente'),
        400: OpenApiResponse(description='Estado inválido'),
        404: OpenApiResponse(description='Solicitud no encontrada')
    }
)
@api_view(['PATCH'])
@permission_classes([permissions.IsAdminUser])
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

@extend_schema(
    tags=['backoffice'],
    description='Obtiene el detalle de una solicitud específica.',
    responses={
        200: SolicitudSerializer
    }
)
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def user_detail(request, user_id):
    solicitud = Solicitud.objects.get(usuario__id=user_id)
    serializer = SolicitudSerializer(solicitud)
    return render(request, 'backoffice/detail.html', {'solicitud': serializer.data})
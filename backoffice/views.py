from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from users.models import CustomUser, Solicitud
from users.serializers import UserSerializer, SolicitudSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from users.models import SolicitudLog
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.hashers import make_password
from django.views.decorators.http import require_http_methods



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
    if estado == 'nuevos':
        # Ahora mostraremos los usuarios con rol 'usuario'
        usuarios_list = CustomUser.objects.filter(rol='usuario').order_by('-date_joined')
    elif estado == 'pendientes':
        solicitudes_list = Solicitud.objects.filter(estado='pendiente').order_by('-fecha_creacion')
    elif estado == 'aprobados':
        solicitudes_list = Solicitud.objects.filter(estado='aceptada').order_by('-fecha_creacion')
    elif estado == 'rechazados':
        solicitudes_list = Solicitud.objects.filter(estado='rechazada').order_by('-fecha_creacion')
    else:
        solicitudes_list = Solicitud.objects.filter(estado='pendiente').order_by('-fecha_creacion')
    
    # Configurar la paginación
    page = request.GET.get('page', 1)
    items_per_page = 5
    
    if estado == 'nuevos':
        paginator = Paginator(usuarios_list, items_per_page)
    else:
        paginator = Paginator(solicitudes_list, items_per_page)
    
    try:
        if estado == 'nuevos':
            usuarios_paginados = paginator.page(page)
        else:
            solicitudes = paginator.page(page)
    except PageNotAnInteger:
        if estado == 'nuevos':
            usuarios_paginados = paginator.page(1)
        else:
            solicitudes = paginator.page(1)
    except EmptyPage:
        if estado == 'nuevos':
            usuarios_paginados = paginator.page(paginator.num_pages)
        else:
            solicitudes = paginator.page(paginator.num_pages)
    
    # Obtener contadores para la sidebar
    usuarios_count = CustomUser.objects.filter(rol='usuario').count()
    solicitudes_pendientes_count = Solicitud.objects.filter(estado='pendiente').count()
    solicitudes_aprobadas_count = Solicitud.objects.filter(estado='aceptada').count()
    solicitudes_rechazadas_count = Solicitud.objects.filter(estado='rechazada').count()
    
    return render(request, 'backoffice/dashboard.html', {
        'nuevos': usuarios_paginados if estado == 'nuevos' else None,
        'pendientes': solicitudes if estado == 'pendientes' else None,
        'aprobados': solicitudes if estado == 'aprobados' else None,
        'rechazados': solicitudes if estado == 'rechazados' else None,
        'nuevos_count': usuarios_count,
        'pendientes_count': solicitudes_pendientes_count,
        'aprobados_count': solicitudes_aprobadas_count,
        'rechazados_count': solicitudes_rechazadas_count,
        'estado': estado,
        'page_obj': usuarios_paginados if estado == 'nuevos' else solicitudes,
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



@login_required
@require_http_methods(["POST"])
def add_user(request):
    if request.method == 'POST':
        # Obtener datos del formulario
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        rol = request.POST.get('rol')
        
        # Validar que todos los campos estén presentes
        if not first_name or not last_name or not email or not password:
            return redirect('dashboard')
        
        # Validar que el correo no exista
        if CustomUser.objects.filter(email=email).exists():
            return redirect('dashboard')
            
        try:
            # Crear usuario
            user = CustomUser.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=email,  # Usamos el email como username
                password=make_password(password),  # Encriptamos la contraseña
                rol=rol
            )
            
            # Crear solicitud con estado "nuevo"
            Solicitud.objects.create(
                usuario=user,
                descripcion="Usuario creado desde el backoffice",
                estado="nuevo"
            )
            
            # Redirigir a la página de nuevos usuarios
            return redirect('dashboard')
            
        except Exception as e:
            return redirect('dashboard')
    
    # Si es GET, redireccionar a dashboard con estado add_user
    return redirect('dashboard')
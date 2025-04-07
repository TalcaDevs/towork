from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from users.models import Solicitud, CustomUser, SolicitudLog
from users.serializers import UserSerializer, SolicitudSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .forms import CustomUserCreationForm, CustomUserEditForm


def custom_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")
        return render(request, "backoffice/login.html", {"error": "Credenciales inválidas"})
    return render(request, "backoffice/login.html")


@login_required
def dashboard(request):
    estado = request.GET.get('estado', 'pendientes')
    user_id = request.GET.get('user_id')

    if estado in ['card_detail', 'update_status'] and user_id:
        solicitud = get_object_or_404(Solicitud, usuario__id=user_id)
        return render(request, 'backoffice/dashboard.html', {'estado': estado, 'solicitud': solicitud})

    estado_mapping = {
        'pendientes': 'pendiente',
        'aprobados': 'aceptada',
        'rechazados': 'rechazada'
    }
    solicitudes_list = Solicitud.objects.filter(
        estado=estado_mapping.get(estado, 'pendiente')
    ).order_by('-fecha_creacion')

    paginator = Paginator(solicitudes_list, 5)
    page = request.GET.get('page', 1)
    try:
        solicitudes = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        solicitudes = paginator.page(1)

    context = {
        estado: solicitudes,
        'pendientes_count': Solicitud.objects.filter(estado='pendiente').count(),
        'aprobados_count': Solicitud.objects.filter(estado='aceptada').count(),
        'rechazados_count': Solicitud.objects.filter(estado='rechazada').count(),
        'estado': estado,
        'page_obj': solicitudes,
        'paginator': paginator,
    }
    return render(request, 'backoffice/dashboard.html', context)


@login_required
def update_status(request, user_id):
    solicitud = get_object_or_404(Solicitud, usuario__id=user_id)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        SolicitudLog.objects.create(
            solicitud=solicitud,
            usuario=request.user,
            estado_anterior=solicitud.estado,
            nuevo_estado=nuevo_estado
        )
        solicitud.estado = nuevo_estado
        solicitud.save()
        return redirect('dashboard')
    return render(request, 'backoffice/update_status.html', {'solicitud': solicitud})


@extend_schema(tags=['backoffice'], description='Obtiene la lista de usuarios.', responses={200: UserSerializer(many=True)})
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def user_list(request):
    users = CustomUser.objects.all()
    return Response(UserSerializer(users, many=True).data)


@extend_schema(
    tags=['backoffice'],
    description='Cambia el estado de una solicitud.',
    request={'application/json': {'type': 'object','properties': {'estado': {'type': 'string', 'enum': ['pendiente', 'aceptada', 'rechazada']}}, 'required': ['estado']}},
    responses={200: OpenApiResponse(description='Actualizado'), 400: OpenApiResponse(description='Inválido'), 404: OpenApiResponse(description='No encontrado')})
@api_view(['PATCH'])
@permission_classes([permissions.IsAdminUser])
def change_request_status(request, user_id):
    try:
        solicitud = Solicitud.objects.get(usuario__id=user_id)
        nuevo_estado = request.data.get("estado")
        if nuevo_estado not in ["pendiente", "aceptada", "rechazada"]:
            return Response({"error": "Estado inválido"}, status=status.HTTP_400_BAD_REQUEST)
        solicitud.estado = nuevo_estado
        solicitud.save()
        return Response({"message": "Estado actualizado"})
    except Solicitud.DoesNotExist:
        return Response({"error": "No encontrada"}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(tags=['backoffice'], description='Detalle de solicitud', responses={200: SolicitudSerializer})
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def user_detail(request, user_id):
    solicitud = get_object_or_404(Solicitud, usuario__id=user_id)
    return render(request, 'backoffice/detail.html', {'solicitud': SolicitudSerializer(solicitud).data})


@login_required
def administrar_usuarios(request):
    usuarios_list = CustomUser.objects.all().order_by('-date_joined')
    paginator = Paginator(usuarios_list, 10)
    page = request.GET.get('page', 1)
    try:
        usuarios = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        usuarios = paginator.page(1)

    return render(request, 'backoffice/dashboard.html', {
        'estado': 'administrar_usuarios',
        'users': usuarios,
        'pendientes_count': Solicitud.objects.filter(estado='pendiente').count(),
        'aprobados_count': Solicitud.objects.filter(estado='aceptada').count(),
        'rechazados_count': Solicitud.objects.filter(estado='rechazada').count()
    })


@login_required
def toggle_usuario_estado(request, user_id):
    usuario = get_object_or_404(CustomUser, id=user_id)
    usuario.is_active = not usuario.is_active
    usuario.save()
    return redirect('/?estado=administrar_usuarios')


@login_required
def crear_usuario(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect(f'/?estado=user_form&success=Usuario {user.first_name} {user.last_name} creado correctamente.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'backoffice/dashboard.html', {
        'estado': 'user_form',
        'user_form': form,
        'pendientes_count': Solicitud.objects.filter(estado='pendiente').count(),
        'aprobados_count': Solicitud.objects.filter(estado='aceptada').count(),
        'rechazados_count': Solicitud.objects.filter(estado='rechazada').count()
    })


@login_required
def editar_usuario(request, user_id):
    usuario = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, instance=usuario)
        if form.is_valid():
            user = form.save()
            return redirect(f'/?estado=user_form&user_id={user.id}&success=Usuario {user.first_name} {user.last_name} actualizado correctamente.')
    else:
        form = CustomUserEditForm(instance=usuario)

    return render(request, 'backoffice/dashboard.html', {
        'estado': 'user_form',
        'user_form': form,
        'pendientes_count': Solicitud.objects.filter(estado='pendiente').count(),
        'aprobados_count': Solicitud.objects.filter(estado='aceptada').count(),
        'rechazados_count': Solicitud.objects.filter(estado='rechazada').count()
    })
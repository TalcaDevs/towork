from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from users.models import CustomUser, Request
from users.serializers import UserSerializer, RequestSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from users.models import RequestLog
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.hashers import make_password
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.contrib import messages
import logging

# ✅ NUEVO: Importar función de sincronización
from users.utils import sync_user_to_public_profile, delete_public_profile

logger = logging.getLogger(__name__)


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
    status_param = request.GET.get('status', 'pending')
    user_id = request.GET.get('user_id')
    request_obj = None
    
    if status_param in ['card_detail', 'update_status'] and user_id:
        request_obj = Request.objects.get(user__id=user_id)
        return render(request, 'backoffice/dashboard.html', {
            'status': status_param,
            'request': request_obj,
        })
    
    if status_param == 'new':
        requests_list = Request.objects.filter(status='new').order_by('-created_date')
        users_list = CustomUser.objects.filter(
            id__in=requests_list.values_list('user_id', flat=True)
        ).order_by('-date_joined')
    elif status_param == 'pending':
        requests_list = Request.objects.filter(status='pending').order_by('-created_date')
    elif status_param == 'accepted':
        requests_list = Request.objects.filter(status='accepted').order_by('-created_date')
    elif status_param == 'rejected':
        requests_list = Request.objects.filter(status='rejected').order_by('-created_date')
    else:
        requests_list = Request.objects.filter(status='pending').order_by('-created_date')
    
    page = request.GET.get('page', 1)
    items_per_page = 5
    
    if status_param == 'new':
        paginator = Paginator(users_list, items_per_page)
    else:
        paginator = Paginator(requests_list, items_per_page)
    
    try:
        if status_param == 'new':
            paginated_users = paginator.page(page)
        else:
            requests = paginator.page(page)
    except PageNotAnInteger:
        if status_param == 'new':
            paginated_users = paginator.page(1)
        else:
            requests = paginator.page(1)
    except EmptyPage:
        if status_param == 'new':
            paginated_users = paginator.page(paginator.num_pages)
        else:
            requests = paginator.page(paginator.num_pages)
    
    new_count = Request.objects.filter(status='new').count()
    pending_requests_count = Request.objects.filter(status='pending').count()
    accepted_requests_count = Request.objects.filter(status='accepted').count()
    rejected_requests_count = Request.objects.filter(status='rejected').count()
    
    return render(request, 'backoffice/dashboard.html', {
        'new': paginated_users if status_param == 'new' else None,
        'pending': requests if status_param == 'pending' else None,
        'accepted': requests if status_param == 'accepted' else None,
        'rejected': requests if status_param == 'rejected' else None,
        'new_count': new_count,
        'pending_count': pending_requests_count,
        'accepted_count': accepted_requests_count,
        'rejected_count': rejected_requests_count,
        'status': status_param,
        'page_obj': paginated_users if status_param == 'new' else requests,
        'paginator': paginator,
    })

@login_required
def update_status(request, user_id):
    """
    ✅ ACTUALIZADA: Función con sincronización automática
    """
    if request.method == 'POST':
        new_status = request.POST.get('status')
        
        try:
            request_obj = Request.objects.get(user__id=user_id)
            previous_status = request_obj.status
            
            # ✅ NUEVO: Verificar si hubo cambio de estado
            if previous_status == new_status:
                logger.info(f"No hay cambio de estado para usuario {user_id}. Estado actual: {new_status}")
                return redirect('dashboard')
            
            # Actualizar el estado
            request_obj.status = new_status
            request_obj.save()
            
            # Crear log del cambio
            RequestLog.objects.create(
                request=request_obj,
                user=request.user,
                previous_status=previous_status,
                new_status=new_status
            )
            
            user_name = f"{request_obj.user.first_name} {request_obj.user.last_name}"
            
            # ✅ NUEVO: Lógica de sincronización según el nuevo estado
            if new_status == 'accepted':
                # 🟢 APROBADO: Sincronizar a tablas públicas
                logger.info(f"Aprobando usuario {user_id} - Iniciando sincronización...")
                
                success, sync_message, public_profile = sync_user_to_public_profile(user_id)
                
                if success:
                    success_msg = f"Usuario {user_name} aprobado y sincronizado exitosamente. {sync_message}"
                    logger.info(success_msg)
                    return redirect(f"{reverse('dashboard')}?status=accepted&message={success_msg}&message_type=success")
                else:
                    error_msg = f"Usuario {user_name} aprobado pero falló la sincronización: {sync_message}"
                    logger.error(error_msg)
                    return redirect(f"{reverse('dashboard')}?status=accepted&message={error_msg}&message_type=error")
                    
            elif new_status == 'rejected':
                # 🔴 RECHAZADO: Eliminar de tablas públicas si existía
                logger.info(f"Rechazando usuario {user_id} - Eliminando perfil público si existe...")
                
                success, delete_message = delete_public_profile(user_id)
                
                if success:
                    success_msg = f"Usuario {user_name} rechazado. {delete_message}"
                    logger.info(success_msg)
                    return redirect(f"{reverse('dashboard')}?status=rejected&message={success_msg}&message_type=success")
                else:
                    error_msg = f"Usuario {user_name} rechazado pero hubo un error: {delete_message}"
                    logger.error(error_msg)
                    return redirect(f"{reverse('dashboard')}?status=rejected&message={error_msg}&message_type=error")
                    
            elif new_status == 'pending':
                # 🟡 PENDIENTE: Eliminar de tablas públicas si existía (volvió a revisión)
                logger.info(f"Usuario {user_id} vuelve a estado pendiente - Eliminando perfil público...")
                
                success, delete_message = delete_public_profile(user_id)
                
                success_msg = f"Usuario {user_name} cambió a pendiente. {delete_message}"
                logger.info(success_msg)
                return redirect(f"{reverse('dashboard')}?status=pending&message={success_msg}&message_type=success")
                
            else:
                # Estado no reconocido
                logger.warning(f"Estado no reconocido: {new_status} para usuario {user_id}")
                return redirect(f"{reverse('dashboard')}?status=pending&message=Estado actualizado&message_type=success")
                
        except Request.DoesNotExist:
            error_msg = f"No se encontró solicitud para el usuario {user_id}"
            logger.error(error_msg)
            return redirect(f"{reverse('dashboard')}?status=pending&message={error_msg}&message_type=error")
            
        except Exception as e:
            error_msg = f"Error inesperado al actualizar estado de usuario {user_id}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return redirect(f"{reverse('dashboard')}?status=pending&message={error_msg}&message_type=error")
    
    else:
        # GET request - mostrar formulario
        try:
            request_obj = Request.objects.get(user__id=user_id)
            return render(request, 'backoffice/update_status.html', {'request': request_obj})
        except Request.DoesNotExist:
            return redirect('dashboard')

@extend_schema(
    tags=['backoffice'],
    description='Gets the list of users with all their information.',
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
    description='Endpoint to change the status of a user request (pending, accepted, rejected).',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'status': {'type': 'string', 'enum': ['pending', 'accepted', 'rejected']}
            },
            'required': ['status']
        }
    },
    responses={
        200: OpenApiResponse(description='Request status updated successfully'),
        400: OpenApiResponse(description='Invalid status'),
        404: OpenApiResponse(description='Request not found')
    }
)

@login_required
@require_http_methods(["POST"])
def delete_user(request, user_id):
    """
    ✅ ACTUALIZADA: Función con eliminación de perfil público
    """
    if not request.user.is_staff and request.user.role != 'admin':
        return redirect('dashboard')
        
    try:
        user_to_delete = CustomUser.objects.get(id=user_id)
        user_name = f"{user_to_delete.first_name} {user_to_delete.last_name}"
        
        # ✅ NUEVO: Eliminar perfil público antes de eliminar usuario
        logger.info(f"Eliminando usuario {user_id} - Eliminando perfil público primero...")
        success, delete_message = delete_public_profile(user_id)
        
        if not success:
            logger.warning(f"No se pudo eliminar perfil público de usuario {user_id}: {delete_message}")
        
        # Create deletion log before deleting the user
        from users.models import UserDeletionLog
        UserDeletionLog.objects.create(
            deleted_user_id=user_id,
            deleted_by=request.user
        )
        
        user_to_delete.delete()
        
        success_msg = f"Usuario {user_name} eliminado correctamente (incluyendo perfil público)"
        logger.info(success_msg)
        return redirect(f"{reverse('dashboard')}?status=pending&message={success_msg}&message_type=success")
        
    except CustomUser.DoesNotExist:
        error_msg = "Error: El usuario no existe"
        return redirect(f"{reverse('dashboard')}?status=pending&message={error_msg}&message_type=error")
    except Exception as e:
        error_msg = f"Error al eliminar usuario: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return redirect(f"{reverse('dashboard')}?status=pending&message={error_msg}&message_type=error")

@api_view(['PATCH'])
@permission_classes([permissions.IsAdminUser])
def change_request_status(request, user_id):
    """
    ✅ ACTUALIZADA: Endpoint API con sincronización automática
    """
    try:
        request_obj = Request.objects.get(user__id=user_id)
        new_status = request.data.get("status")

        if new_status not in ["pending", "accepted", "rejected"]:
            return Response({"error": "Estado inválido"}, status=status.HTTP_400_BAD_REQUEST)

        previous_status = request_obj.status
        
        # Verificar si hay cambio de estado
        if previous_status == new_status:
            return Response({"message": "No hay cambio de estado"}, status=status.HTTP_200_OK)

        # Actualizar estado
        request_obj.status = new_status
        request_obj.save()
        
        # Crear log
        RequestLog.objects.create(
            request=request_obj,
            user=request.user,
            previous_status=previous_status,
            new_status=new_status
        )

        # ✅ NUEVO: Lógica de sincronización
        if new_status == 'accepted':
            success, sync_message, public_profile = sync_user_to_public_profile(user_id)
            if success:
                return Response({
                    "message": "Solicitud aprobada y sincronizada exitosamente",
                    "sync_details": sync_message
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "message": "Solicitud aprobada pero falló la sincronización",
                    "error": sync_message
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        elif new_status in ['rejected', 'pending']:
            success, delete_message = delete_public_profile(user_id)
            return Response({
                "message": f"Estado de solicitud actualizado a {new_status}",
                "public_profile_action": delete_message
            }, status=status.HTTP_200_OK)

        return Response({"message": "Estado de solicitud actualizado correctamente"}, status=status.HTTP_200_OK)

    except Request.DoesNotExist:
        return Response({"error": "Solicitud no encontrada para este usuario"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error en change_request_status para usuario {user_id}: {str(e)}", exc_info=True)
        return Response({"error": "Error interno del servidor"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
    tags=['backoffice'],
    description='Gets the details of a specific request.',
    responses={
        200: RequestSerializer
    }
)
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def user_detail(request, user_id):
    request_obj = Request.objects.get(user__id=user_id)
    serializer = RequestSerializer(request_obj)
    return render(request, 'backoffice/detail.html', {'request': serializer.data})


@login_required
@require_http_methods(["POST"])
def add_user(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        if not first_name or not last_name or not email or not password:
            return redirect('dashboard')
        
        if CustomUser.objects.filter(email=email).exists():
            return redirect('dashboard')
            
        try:
            user = CustomUser.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=email,
                password=make_password(password),  
                role=role
            )
            
            Request.objects.create(
                user=user,
                description="Usuario creado desde el backoffice",
                status="new"
            )
            
            return redirect('dashboard')
            
        except Exception as e:
            return redirect('dashboard')
    
    return redirect('dashboard')
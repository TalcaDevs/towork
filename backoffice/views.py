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
    if request.method == 'POST':
        new_status = request.POST.get('status')
        request_obj = Request.objects.get(user__id=user_id)
        previous_status = request_obj.status
        request_obj.status = new_status
        request_obj.save()

        RequestLog.objects.create(
            request=request_obj,
            user=request.user,
            previous_status=previous_status,
            new_status=new_status
        )

        return redirect('dashboard')
    else:
        request_obj = Request.objects.get(user__id=user_id)
        return render(request, 'backoffice/update_status.html', {'request': request_obj})

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
    if not request.user.is_staff and request.user.role != 'admin':
        return redirect('dashboard')
        
    try:
        user_to_delete = CustomUser.objects.get(id=user_id)
        user_name = f"{user_to_delete.first_name} {user_to_delete.last_name}"
        
        # Create deletion log before deleting the user
        from users.models import UserDeletionLog
        UserDeletionLog.objects.create(
            deleted_user_id=user_id,
            deleted_by=request.user
        )
        
        user_to_delete.delete()
        return redirect(f"{reverse('dashboard')}?status=pending&message=Usuario {user_name} eliminado correctamente&message_type=success")
        
    except CustomUser.DoesNotExist:
        return redirect(f"{reverse('dashboard')}?status=pending&message=Error: El usuario no existe&message_type=error")
    except Exception as e:
        return redirect(f"{reverse('dashboard')}?status=pending&message=Error al eliminar usuario: {str(e)}&message_type=error")

@api_view(['PATCH'])
@permission_classes([permissions.IsAdminUser])
def change_request_status(request, user_id):
    try:
        request_obj = Request.objects.get(user__id=user_id)
        new_status = request.data.get("status")

        if new_status not in ["pending", "accepted", "rejected"]:
            return Response({"error": "Estado inválido"}, status=status.HTTP_400_BAD_REQUEST)

        request_obj.status = new_status
        request_obj.save()

        return Response({"message": "Estado de solicitud actualizado correctamente"}, status=status.HTTP_200_OK)

    except Request.DoesNotExist:
        return Response({"error": "Solicitud no encontrada para este usuario"}, status=status.HTTP_404_NOT_FOUND)

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
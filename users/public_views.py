"""
Vistas para endpoints públicos - Solo datos aprobados
"""
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.http import require_GET
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .models import UserPublicProfile
from .public_serializers import (
    UserPublicProfileSerializer, 
    UserPublicProfileSummarySerializer,
    PublicProfileStatsSerializer
)
from .utils import get_public_profile_stats


@extend_schema(
    tags=['public'],
    operation_id='get-public-profile',
    summary='Get public user profile by ID',
    description='Gets the complete public profile of a user by their original user ID. Only returns approved data.',
    parameters=[
        OpenApiParameter(
            name='user_id',
            description='Original user ID (from CustomUser table)',
            required=True,
            type=int,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        200: UserPublicProfileSerializer,
        404: OpenApiResponse(description='User not found or not approved')
    }
)
@require_GET
@api_view(['GET'])
@permission_classes([permissions.AllowAny])  # ✅ Público, no requiere autenticación
def get_public_profile(request, user_id):
    """
    Obtiene el perfil público completo de un usuario por su ID original
    """
    try:
        # Buscar por original_user_id, no por el ID del perfil público
        public_profile = get_object_or_404(
            UserPublicProfile.objects.prefetch_related(
                'education',
                'work_experience', 
                'certifications',
                'projects',
                'skills__skill',
                'languages__language'
            ),
            original_user_id=user_id
        )
        
        serializer = UserPublicProfileSerializer(public_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"error": "Error interno del servidor"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=['public'],
    operation_id='get-public-profile-by-public-id',
    summary='Get public user profile by public profile ID',
    description='Gets the complete public profile by the public profile ID (not original user ID).',
    parameters=[
        OpenApiParameter(
            name='public_id',
            description='Public profile ID (from UserPublicProfile table)',
            required=True,
            type=int,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        200: UserPublicProfileSerializer,
        404: OpenApiResponse(description='Public profile not found')
    }
)
@require_GET
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_public_profile_by_public_id(request, public_id):
    """
    Obtiene el perfil público completo por el ID del perfil público
    """
    try:
        public_profile = get_object_or_404(
            UserPublicProfile.objects.prefetch_related(
                'education',
                'work_experience', 
                'certifications',
                'projects',
                'skills__skill',
                'languages__language'
            ),
            id=public_id
        )
        
        serializer = UserPublicProfileSerializer(public_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"error": "Error interno del servidor"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=['public'],
    operation_id='list-public-profiles',
    summary='List all public profiles',
    description='Gets a paginated list of all approved public profiles with basic information.',
    parameters=[
        OpenApiParameter(
            name='page',
            description='Page number',
            required=False,
            type=int,
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name='page_size',
            description='Number of profiles per page (max 50)',
            required=False,
            type=int,
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name='search',
            description='Search by name, location, or role',
            required=False,
            type=str,
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name='role',
            description='Filter by role',
            required=False,
            type=str,
            enum=['admin', 'user', 'moderator'],
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name='location',
            description='Filter by location (contains)',
            required=False,
            type=str,
            location=OpenApiParameter.QUERY
        ),
    ],
    responses={
        200: OpenApiResponse(
            description='Paginated list of public profiles',
            examples={
                'application/json': {
                    'count': 150,
                    'next': 'http://example.com/public/profiles/?page=3',
                    'previous': 'http://example.com/public/profiles/?page=1',
                    'results': [
                        {
                            'id': 1,
                            'original_user_id': 42,
                            'first_name': 'Juan',
                            'last_name': 'Pérez',
                            'profile_photo': 'https://example.com/photo.jpg',
                            'description': 'Desarrollador Full Stack...',
                            'location': 'Ciudad de México',
                            'role': 'user',
                            'skills_count': 8,
                            'projects_count': 3,
                            'experience_years': 2.5
                        }
                    ]
                }
            }
        )
    }
)
@require_GET
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def list_public_profiles(request):
    """
    Lista todos los perfiles públicos con paginación y filtros
    """
    try:
        # Obtener parámetros de query
        page = request.GET.get('page', 1)
        page_size = min(int(request.GET.get('page_size', 20)), 50)  # Máximo 50 por página
        search = request.GET.get('search', '')
        role_filter = request.GET.get('role', '')
        location_filter = request.GET.get('location', '')
        
        # Query base
        queryset = UserPublicProfile.objects.all().order_by('-published_at')
        
        # Aplicar filtros
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(description__icontains=search) |
                Q(location__icontains=search)
            )
        
        if role_filter:
            queryset = queryset.filter(role=role_filter)
            
        if location_filter:
            queryset = queryset.filter(location__icontains=location_filter)
        
        # Paginación
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        # Serializar
        serializer = UserPublicProfileSummarySerializer(page_obj.object_list, many=True)
        
        # Respuesta paginada
        return Response({
            'count': paginator.count,
            'next': page_obj.next_page_number() if page_obj.has_next() else None,
            'previous': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'results': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"error": "Error interno del servidor"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=['public'],
    operation_id='get-public-profiles-stats',
    summary='Get public profiles statistics',
    description='Gets general statistics about approved public profiles.',
    responses={
        200: PublicProfileStatsSerializer
    }
)
@require_GET
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_public_profiles_stats(request):
    """
    Obtiene estadísticas generales de los perfiles públicos
    """
    try:
        stats = get_public_profile_stats()
        
        if not stats:
            return Response(
                {"error": "No se pudieron obtener las estadísticas"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Agregar timestamp de la consulta más reciente
        if UserPublicProfile.objects.exists():
            stats['last_updated'] = UserPublicProfile.objects.latest('last_updated').last_updated
        else:
            stats['last_updated'] = None
            
        serializer = PublicProfileStatsSerializer(stats)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"error": "Error interno del servidor"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=['public'],
    operation_id='search-public-profiles',
    summary='Search public profiles by skills',
    description='Search public profiles by skills, location, and other criteria.',
    parameters=[
        OpenApiParameter(
            name='skills',
            description='Comma-separated list of skills to search for',
            required=False,
            type=str,
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name='location',
            description='Location to search in',
            required=False,
            type=str,
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name='min_experience',
            description='Minimum years of experience',
            required=False,
            type=float,
            location=OpenApiParameter.QUERY
        ),
    ],
    responses={
        200: UserPublicProfileSummarySerializer(many=True)
    }
)
@require_GET
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_public_profiles(request):
    """
    Búsqueda avanzada de perfiles públicos por habilidades y otros criterios
    """
    try:
        skills_param = request.GET.get('skills', '')
        location_param = request.GET.get('location', '')
        min_experience = request.GET.get('min_experience', 0)
        
        queryset = UserPublicProfile.objects.all()
        
        # Filtrar por habilidades
        if skills_param:
            skills_list = [skill.strip() for skill in skills_param.split(',')]
            for skill in skills_list:
                queryset = queryset.filter(skills__skill__name__icontains=skill)
        
        # Filtrar por ubicación
        if location_param:
            queryset = queryset.filter(location__icontains=location_param)
        
        # Eliminar duplicados y ordenar
        queryset = queryset.distinct().order_by('-published_at')
        
        # Serializar (limitamos a 100 resultados por performance)
        serializer = UserPublicProfileSummarySerializer(queryset[:100], many=True)
        
        # Filtrar por experiencia mínima en el lado de Python (más flexible)
        if min_experience:
            try:
                min_exp = float(min_experience)
                filtered_results = [
                    profile for profile in serializer.data 
                    if profile.get('experience_years', 0) >= min_exp
                ]
                return Response(filtered_results, status=status.HTTP_200_OK)
            except ValueError:
                pass
        
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"error": "Error interno del servidor"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
"""
URLs para endpoints públicos - Solo datos aprobados
"""
from django.urls import path
from .public_views import (
    get_public_profile,
    get_public_profile_by_public_id,
    list_public_profiles,
    get_public_profiles_stats,
    search_public_profiles
)

urlpatterns = [
    # Obtener perfil público por ID de usuario original
    path('get-profile/<int:user_id>/', get_public_profile, name='get_public_profile'),
    
    # Obtener perfil público por ID del perfil público
    path('profile/<int:public_id>/', get_public_profile_by_public_id, name='get_public_profile_by_id'),
    
    # Listar todos los perfiles públicos (con paginación y filtros)
    path('profiles/', list_public_profiles, name='list_public_profiles'),
    
    # Búsqueda avanzada de perfiles públicos
    path('search/', search_public_profiles, name='search_public_profiles'),
    
    # Estadísticas generales de perfiles públicos
    path('stats/', get_public_profiles_stats, name='get_public_profiles_stats'),
]
from django.urls import path
from backoffice.views import (
    custom_login, dashboard, update_status,
    user_list, change_request_status, user_detail,
    crear_usuario, editar_usuario, toggle_usuario_estado
)
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', custom_login, name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('', dashboard, name="dashboard"),
    path('users/', user_list, name="listar_usuarios"),
    path('users/<int:user_id>/estado/', change_request_status, name="cambiar_estado_usuario"),
    path('users/<int:user_id>/', user_detail, name="detalle_usuario"),
    path('update_status/<int:user_id>/', update_status, name='update_status'),
    
    # Rutas para la gestión de usuarios
    path('crear-usuario/', crear_usuario, name='crear_usuario'),
    path('editar-usuario/<int:user_id>/', editar_usuario, name='editar_usuario'),
    path('toggle-usuario-estado/<int:user_id>/', toggle_usuario_estado, name='toggle_usuario_estado'),
]
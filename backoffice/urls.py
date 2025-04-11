from django.urls import path
from backoffice.views import (
    custom_login, dashboard, 
    update_status_form, update_status_submit,
    user_list, change_request_status, user_detail, user_detail_api,
    crear_usuario_form, crear_usuario_submit, 
    editar_usuario_form, editar_usuario_submit, 
    toggle_usuario_estado, administrar_usuarios
)
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # Authentication routes
    path('login/', custom_login, name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    
    # Dashboard
    path('', dashboard, name="dashboard"),
    
    # API routes
    path('api/users/', user_list, name="listar_usuarios"),
    path('api/users/<int:user_id>/estado/', change_request_status, name="cambiar_estado_usuario"),
    path('api/users/<int:user_id>/', user_detail_api, name="detalle_usuario_api"),
    
    # User detail routes
    path('users/<int:user_id>/', user_detail, name="detalle_usuario"),
    
    # Status update routes - separated for GET and POST
    path('update_status/<int:user_id>/', update_status_form, name='update_status_form'),
    path('update_status/<int:user_id>/submit/', update_status_submit, name='update_status_submit'),
    
    # User management routes
    path('administrar-usuarios/', administrar_usuarios, name='administrar_usuarios'),
    
    # Create user routes - separated for GET and POST
    path('crear-usuario/', crear_usuario_form, name='crear_usuario_form'),
    path('crear-usuario/submit/', crear_usuario_submit, name='crear_usuario_submit'),
    
    # Edit user routes - separated for GET and POST
    path('editar-usuario/<int:user_id>/', editar_usuario_form, name='editar_usuario_form'),
    path('editar-usuario/<int:user_id>/submit/', editar_usuario_submit, name='editar_usuario_submit'),
    
    # Toggle user status
    path('toggle-usuario-estado/<int:user_id>/', toggle_usuario_estado, name='toggle_usuario_estado'),
]
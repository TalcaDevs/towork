from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import guardar_perfil_completo, obtener_usuarios, registro_usuario, login_usuario, obtener_perfil_completo

urlpatterns = [ 
    path('', obtener_usuarios, name="obtener_usuarios"), 
    path('signup/', registro_usuario, name="registro_usuario"),
    path('signin/', login_usuario, name="login_usuario"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('get-profile/', obtener_perfil_completo, name="obtener_informacion_usuario"),
    path('save-profile/', guardar_perfil_completo, name="guardar_perfil"),
]

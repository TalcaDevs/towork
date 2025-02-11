from django.urls import path
from backoffice.views import custom_login, dashboard
from django.contrib.auth.views import LogoutView
from backoffice.views import user_list, change_request_status

urlpatterns = [
    path('login/', custom_login, name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('', dashboard, name="dashboard"),
    path('users/', user_list, name="listar_usuarios"),
    path('users/<int:user_id>/estado/', change_request_status, name="cambiar_estado_usuario"),
]

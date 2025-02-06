from django.urls import path
from .views import guardar_perfil_completo
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [ 
    path('save-profile/', guardar_perfil_completo, name="guardar_perfil"),
]

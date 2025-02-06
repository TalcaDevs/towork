from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import SolicitudViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'solicitudes', SolicitudViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Obtener access y refresh tokens
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), 
]

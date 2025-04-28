from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import SolicitudViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users.views import listar_solicitudes
from .schema import urlpatterns as schema_urlpatterns

router = DefaultRouter()
router.register(r'solicitudes', SolicitudViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), 
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), 
    path('requests/', listar_solicitudes, name='listar_solicitudes'),
]

urlpatterns += schema_urlpatterns
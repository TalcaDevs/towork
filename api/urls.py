from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import RequestViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users.views import list_requests
from .schema import urlpatterns as schema_urlpatterns

router = DefaultRouter()
router.register(r'requests', RequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), 
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), 
    path('requests/', list_requests, name='list_requests'),
]

urlpatterns += schema_urlpatterns
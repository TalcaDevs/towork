from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import RequestViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users.views import list_requests
from .schema import urlpatterns as schema_urlpatterns
from .views import RequestViewSet, save_template, user_template


router = DefaultRouter()
router.register(r'requests', RequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), 
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), 
    path('requests/', list_requests, name='list_requests'),
    path('template/save/', save_template, name='save_template'),
    path('template/user/', user_template, name='user_template'),
]

urlpatterns += schema_urlpatterns
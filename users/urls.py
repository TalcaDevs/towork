from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import save_complete_profile, get_users, register_user, login_user, get_complete_profile

urlpatterns = [ 
    path('', get_users, name="get_users"), 
    path('signup/', register_user, name="register_user"),
    path('signin/', login_user, name="login_user"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('get-profile/', get_complete_profile, name="get_user_info"),
    path('save-profile/', save_complete_profile, name="save_profile"),
]
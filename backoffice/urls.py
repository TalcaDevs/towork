from django.urls import path
from backoffice.views import custom_login, dashboard
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', custom_login, name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('', dashboard, name="dashboard"),
]

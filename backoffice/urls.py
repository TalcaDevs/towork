from django.urls import path
from backoffice.views import custom_login, dashboard, update_status
from django.contrib.auth.views import LogoutView
from backoffice.views import custom_login, dashboard, update_status, user_list, change_request_status, user_detail, add_user, delete_user

urlpatterns = [
    path('login/', custom_login, name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('', dashboard, name="dashboard"),
    path('users/', user_list, name="list_users"),
    path('users/<int:user_id>/status/', change_request_status, name="change_user_status"),
    path('users/<int:user_id>/', user_detail, name="user_detail"),
    path('update_status/<int:user_id>/', update_status, name='update_status'),
    path('add_user/', add_user, name='add_user'),
    path('delete_user/<int:user_id>/', delete_user, name='delete_user'), 
]
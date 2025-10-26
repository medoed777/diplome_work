from users.apps import UsersConfig
# from users.views import RegisterView, VerifyCodeView, UserProfileView
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView


app_name = UsersConfig.name


urlpatterns = [
    path("", include("users.urls", namespace="users")),
]
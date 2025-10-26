from users.apps import UsersConfig
# from users.views import RegisterView, VerifyCodeView, UserProfileView
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView


app_name = UsersConfig.name
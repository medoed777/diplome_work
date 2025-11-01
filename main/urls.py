from django.urls import path
from main.apps import MainConfig
from main.views import ProfileView, main_page
from users.views import PhoneLoginView, PhoneConfirmView
from django.contrib.auth import views as auth_views


app_name = MainConfig.name

urlpatterns = [
    path("", main_page, name="base"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("phone-login/", PhoneLoginView.as_view(), name="phone_login"),
    path("phone-confirm/", PhoneConfirmView.as_view(), name="phone_confirm"),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="main:base"),
        name="logout",
    ),
]

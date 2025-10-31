from django.urls import path
from main.apps import MainConfig
from main.views import ProfileView, UserListView, EnterInvaiteCodeView
from users.views import PhoneLoginView, PhoneConfirmView
from django.contrib.auth import views as auth_views


app_name = MainConfig.name

urlpatterns = [
    path("", ProfileView.as_view(), name="profile"),
    path("phone-login/", PhoneLoginView.as_view(), name="phone_login"),
    path("phone-confirm/", PhoneConfirmView.as_view(), name="phone_confirm"),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="main:index"),
        name="logout",
    ),
    path("invaite-code/", EnterInvaiteCodeView.as_view(), name="invaite_code"),
    path("users/", UserListView.as_view(), name="users_list"),
]

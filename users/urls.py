from django.urls import path
from users.views import SendCodeView


urlpatterns = [
    path('api/send_code/', SendCodeView.as_view())
]
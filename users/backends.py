from django.contrib.auth.backends import ModelBackend
from users.models import User


class PhoneBackend(ModelBackend):
    def get_user(self, user_id: int) -> User:
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, request, username: str = None, password: str = None, **kwargs) -> User:
        if username and password:
            try:
                user = User.objects.get(phone=username)
                if user.check_code(password):
                    return user
            except User.DoesNotExist:
                return None
        return None
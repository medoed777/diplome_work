from django.contrib.auth.backends import ModelBackend
from django.core.cache import cache
from users.models import User


class PhoneBackend(ModelBackend):
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username and password:
            user = User.objects.filter(phone=username).first()
            if user:
                cached_code = cache.get(f"user_{username}_code")
                if user.check_code(password) or password == cached_code:
                    cache.delete(f"user_{username}_code")
                    return user
                else:
                    print("Код не соответствует")
            else:
                print("Пользователь не найден")
        return None

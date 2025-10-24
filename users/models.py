from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string

class User(AbstractUser):
    username = None

    phone = models.CharField(
        max_length = 20, null = False, blank = False, unique = True, verbose_name="Номер телефона",
    )

    USERNAME_FIELD = 'phone'

    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class PhoneCode(models.Model):
    phone = models.CharField(
        max_length=20, null=False, blank=False, unique=True, verbose_name="Номер телефона",
    )

    code = models.CharField(max_length=4, blank = False, verbose_name="Код активации",)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания",)

    class Meta:
        verbose_name = 'Код активации'
        verbose_name_plural = 'Коды активации'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")

    invaite_code = models.CharField(max_length=6, unique=True, null=False, blank=False, verbose_name="Инвайт-код")

    active_invaite_code = models.CharField(max_length=6, verbose_name="Активированный инвайт-код")


    def generate_invate_code(self):
        chars = string.ascii_letters + string.digits
        return "".join([random.choice(chars) for _ in range(6)])

    def save(self, *args, **kwargs):
        if not self.invaite_code:
            self.invaite_code = self.generate_invate_code()
        super().save(*args, **kwargs)


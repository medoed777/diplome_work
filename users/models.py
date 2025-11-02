import random
import string
import time

from django.contrib.auth.models import AbstractUser
from django.core.cache import cache
from django.db import models
from django.db.models import CharField

from users.services import generate_invaite_code


class User(AbstractUser):
    username = None
    phone = CharField(
        unique=True, verbose_name="Номер телефона", help_text="Введите номер телефона"
    )
    invaite_code = models.CharField(
        max_length=6,
        unique=True,
        default=generate_invaite_code,
        verbose_name="Инвайт-код",
    )
    invaited_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invaited_users",
        verbose_name="Инвайт-код пригласившего пользователя",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата первой авторизации"
    )

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    def generate_code(self):
        # time.sleep(2)
        chars = string.digits
        code = "".join([random.choice(chars) for _ in range(4)])
        cache.set(f"user_{self.phone}_code", code, timeout=300)
        return code

    def check_code(self, code):
        cached_code = cache.get(f"user_{self.phone}_code")
        return cached_code == code

    def __str__(self):
        return str(self.phone)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

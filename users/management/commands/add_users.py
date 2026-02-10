from django.core.management import call_command
from django.core.management.base import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = "Добавление данных из фикстур"

    def handle(self, *args, **kwargs):
        User.objects.all().delete()

        call_command("loaddata", "users_fixture.json", format="json")
        self.stdout.write(
            self.style.SUCCESS("Пользователи загружены из фикстур успешно")
        )

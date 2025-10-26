from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdminModel(admin.ModelAdmin):
    list_display = list(f.name for f in User._meta.fields)

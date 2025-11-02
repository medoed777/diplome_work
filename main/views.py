from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView

from main.forms import InvaiteCodeForm
from users.models import User


def main_page(request: HttpRequest) -> HttpResponse:
    return render(request, "main/base.html")


class ProfileView(LoginRequiredMixin, FormView):
    template_name = "main/profile.html"
    form_class = InvaiteCodeForm
    success_url = reverse_lazy("main:profile")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        invaited_users = User.objects.filter(invaited_by=user)
        invaited_users_count = invaited_users.count()

        context["invaited_users"] = invaited_users
        context["user"] = user
        context["invaited_users_count"] = invaited_users_count
        context["form"] = self.form_class()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            return self.form_valid(form)
        else:
            messages.error(request, "Ошибка при обработке формы")
            return self.get(request, *args, **kwargs)

    def form_valid(self, form):
        invaite_code = form.cleaned_data["invaite_code"]
        user = self.request.user

        if user.invaited_by:
            messages.error(self.request, "Вы уже использовали инвайт-код")
            return self.form_invalid(form)

        try:
            invaited_by_user = User.objects.get(invaite_code=invaite_code)

        except User.DoesNotExist:
            messages.error(self.request, "Неверный инвайт-код")
            return self.form_invalid(form)

        if invaited_by_user == user:
            messages.error(
                self.request, "Вы не можете использовать свой собственный инвайт-код"
            )
            return self.form_invalid(form)

        user.invaited_by = invaited_by_user
        user.save()

        return super().form_valid(form)

    def form_invalid(self, form):
        return self.get(self.request)

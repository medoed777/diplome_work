from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.views.generic import TemplateView, ListView, FormView
from users.models import User
from main.forms import InvaiteCodeForm
from django.contrib import messages
from django.urls import reverse_lazy


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "main/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        invaited_users = User.objects.filter(invaited_by=user)
        invaited_users_count = invaited_users.count()

        context["invaited_users"] = invaited_users
        context["user"] = user
        context["invaited_users_count"] = invaited_users_count
        return context


class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "main/user_list.html"

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseForbidden(
            "Вы не можете просматривать/изменять или удалять этот объект."
        )


class EnterInvaiteCodeView(LoginRequiredMixin, FormView):
    template_name = "main/invaite_code.html"
    form_class = InvaiteCodeForm
    success_url = reverse_lazy("main:profile")

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

        messages.success(self.request, "Инвайт-код успешно применен")
        return super().form_valid(form)

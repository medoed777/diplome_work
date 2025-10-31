from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.views.generic import FormView, View
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from smsaero import SmsAeroException

from config.settings import DEBUG
from users.forms import CodeForm, PhoneLoginForm
from users.models import User
from users.serializers import RegisterSerializer, UserSerializer, VerifyCodeSerializer
from users.services import send_sms


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data["phone"]
            invaited_by_code = serializer.validated_data.get("invaited_by")

            # if User.objects.filter(phone=phone).exists():
            #     return Response(
            #         {"message": "Пользователь с таким номером телефона уже зарегистрирован."},
            #         status=status.HTTP_400_BAD_REQUEST,
            #     )

            user, create = User.objects.get_or_create(phone=phone)

            if invaited_by_code:
                invaited_by_user = User.objects.filter(invaite_code=invaited_by_code).first()
                if invaited_by_user:
                    if user.invaited_by:
                        return Response(
                            {"message": "Инвайт код уже активирован"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    else:
                        user.invaited_by = invaited_by_user
                        user.save()

            try:
                message_code = user.generate_code()
                code = send_sms(phone, message_code)

                if code:
                    response_data = {"message": "Код отправлен"}
                    user.code = message_code
                    user.save()
                    if DEBUG:
                        response_data["debug_code"] = message_code
                    return Response(response_data, status=status.HTTP_200_OK)
            except SmsAeroException:
                return Response(
                    {"message": "Ошибка отправки SMS. Попробуйте позже."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)

        if serializer.is_valid():
            phone = serializer.validated_data["phone"]
            code = serializer.validated_data["code"]
            try:
                user = User.objects.get(phone=phone)
                if user is not None:
                    if user.code == code:
                        refresh = RefreshToken.for_user(user)
                        user.code = None
                        user.save()
                        return Response(
                            {
                                "refresh": str(refresh),
                                "access": str(refresh.access_token),
                                "message": "Авторизация успешна",
                            },
                            status=status.HTTP_200_OK,
                        )
                    else:
                        return Response(
                            {"message": "Неверный код или срок действия истек"},
                            status=status.HTTP_403_FORBIDDEN,
                        )
                else:
                    return Response(
                        {"message": "Код уже использован или срок действия истек"},
                        status=status.HTTP_403_FORBIDDEN,
                    )
            except User.DoesNotExist:
                return Response(
                    {"message": "Пользователь с таким номером телефона не найден"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveAPIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class PhoneLoginView(View):
    template_name = "users/phone_login.html"
    form_class = PhoneLoginForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            phone = form.cleaned_data["phone"]
            request.session["phone"] = phone
            user, created = User.objects.get_or_create(phone=phone)
            code = user.generate_code()
            try:
                send_sms(phone, code)
                return redirect("main:phone_confirm")
            except Exception as e:
                messages.error(request, f"Ошибка отправки SMS: {str(e)}")
                return render(request, self.template_name, {"form": form})

        return render(request, self.template_name, {"form": form})


class PhoneConfirmView(FormView):
    template_name = "users/phone_confirm.html"
    form_class = CodeForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        phone = self.request.session.get("phone")
        if phone:
            cached_code = cache.get(f"user_{phone}_code")
            context["cached_code"] = cached_code
        return context

    def post(self, request, *args, **kwargs):
        phone = request.session.get("phone")
        code = request.POST.get("code")

        if not phone:
            messages.error(
                request, "Сессия истекла. Пожалуйста, введите номер телефона заново."
            )
            return redirect("users:phone_login")

        user = User.objects.filter(phone=phone).first()
        cached_code = cache.get(f"user_{phone}_code")

        if user and code == cached_code:
            user = authenticate(request=request, username=phone, password=code)
            if user is not None:
                login(request, user, backend="users.backends.PhoneBackend")
                return redirect("main:index")
            else:
                form = self.get_form()
                form.add_error("code", "Неверный код")
                return self.form_invalid(form)

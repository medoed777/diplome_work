import string
import time
from django.shortcuts import render
from pyexpat.errors import messages
from rest_framework.views import APIView
from users.serializers import PhoneSerializers, PhoneCodeSerializers
import random
from users.models import User
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


# class RegisterView(APIView):
#     """
#     Эндпоинт для логина в сервис, присваивания инвайт-кода.
#     Ожидает номер телефона.
#     В случае успеха, отправляет код.
#     """
#     permission_classes = [AllowAny]
#     throttle_classes = [PhoneCodeThrottle]  # Ограничение запросов
#
#     @swagger_auto_schema(
#         request_body=RegisterSerializer,
#         responses={
#             200: "Код отправлен",
#             400: "Ошибка валидации",
#             500: "Ошибка отправки SMS"
#         }
#     )
#     def post(self, request):
#         serializer = RegisterSerializer(data=request.data)
#         if serializer.is_valid():
#             phone = serializer.validated_data["phone"]
#             invited_by_code = serializer.validated_data.get("invited_by")
#
#             # Проверяем, существует ли пользователь с таким номером
#             user, created = User.objects.get_or_create(phone=phone)
#
#             if not created:
#                 if user.invited_by and invited_by_code:
#                     return Response(
#                         {
#                             "invited_by": "Инвайт-код уже указан и не может быть изменён."
#                         },
#                         status=status.HTTP_400_BAD_REQUEST,
#                     )
#
#             # Устанавливаем инвайт-код, если он передан и ранее не был установлен
#             if invited_by_code and not user.invited_by:
#                 invited_by_user = User.objects.filter(
#                     invite_code=invited_by_code
#                 ).first()
#                 if invited_by_user:
#                     user.invited_by = invited_by_user
#                     user.save()
#
#             # Отправляем код подтверждения
#             try:
#                 message_code = user.generate_code()
#                 code = send_sms(phone, message_code)
#                 logger.debug(
#                     f"Логин на телефон: {phone}. "
#                     f"Код подтверждения: {message_code}."
#                 )
#                 if code:
#                     response_data = {"message": "Код отправлен"}
#                     if DEBUG:
#                         response_data["debug_code"] = message_code
#                     return Response(response_data, status=status.HTTP_200_OK)
#             except SmsAeroException:
#                 return Response(
#                     {"message": "Ошибка отправки SMS. Попробуйте позже."},
#                     status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 )
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

import string
import time
from django.shortcuts import render
from pyexpat.errors import messages
from rest_framework.views import APIView
from users.serializers import PhoneSerializers, PhoneCodeSerializers
import random
from users.models import PhoneCode, User, Profile
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


class SendCodeView(APIView):

    def post(self, request):
        serializer = PhoneSerializers(data=request.data)
        if serializer.is_valid():
            chars = string.digits
            code_activate = "".join([random.choice(chars) for _ in range(4)])
            phone = serializer.validated_data["phone"]
            time.sleep(2)
            print(f'Ваш код активации {code_activate}')
            PhoneCode.objects.create(phone=phone, code=code_activate)
            return Response({'message': 'Код отправлен на ваш номер телефона'})
        return Response(serializer.errors, status=400)


class VerifiCodeView(APIView):

    def post(self, request):
        serializer = PhoneCodeSerializers(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data["phone"]
            code = serializer.validated_data["code"]
            try:
                phone_code = PhoneCode.objects.get(phone=phone)
            except PhoneCode.DoesNotExist:
                return Response({'error': 'Код не существует'})
            if phone_code.code == code:
                user, created = User.objects.get_or_create(phone = phone)
                if created:
                    Profile.objects.create(user=user)
                refresh = RefreshToken.for_user(user)
                return Response({'refresh': str(refresh),
                                 'access': str(refresh.access_token)}
                                )
            return Response({'error': 'Код не верный'})
        return Response(serializer.errors, status=400)

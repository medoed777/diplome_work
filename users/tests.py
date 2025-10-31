from unittest import TestCase
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.test import Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from smsaero import SmsAeroException
from django.core.cache import cache
from django.contrib import messages

from users.backends import PhoneBackend
from users.forms import PhoneLoginForm
from users.models import User


class RegisterViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(phone="+79999999999")
        self.url = reverse("users:register")
        self.client.force_authenticate(user=self.user)

    def test_register_user_success(self):
        """Проверяет успешную регистрацию нового пользователя"""
        data = {
            "phone": "+1234567890",
            "invaite_code": "123qwe",
            "message": "Код отправлен",
        }
        with patch("users.services.send_sms") as mock_send_sms:
            mock_send_sms.return_value = True
            response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Код отправлен")
        self.assertTrue(User.objects.filter(phone="+1234567890").exists())
        self.assertEqual(User.objects.count(), 2)

    def test_register_user_with_invaition_code(self):
        """Проверяет регистрацию пользователя с использованием инвайт-кода"""
        invaited_user = User.objects.create(phone="+7777777777", invaite_code="qwe123")

        data = {
            "phone": "+66666666666",
            "invaited_by": invaited_user.invaite_code,
        }
        with patch("users.services.send_sms") as mock_send_sms:
            mock_send_sms.return_value = True
            response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Код отправлен")
        self.assertEqual(User.objects.count(), 3)

    def test_register_user_sms_sending_error(self):
        """Проверяет ситуацию, когда происходит ошибка при отправке SMS"""
        data = {
            "phone": "+79961734335",
            "invaite_code": "123456aaa",
        }

        with patch("users.views.send_sms") as mock_send_sms:
            mock_send_sms.side_effect = SmsAeroException
            response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(
            response.data["message"], "Ошибка отправки SMS. Попробуйте позже."
        )
        self.assertEqual(User.objects.count(), 2)


class VerifyCodeViewTests(APITestCase):
    def setUp(self):
        self.phone = "+1234567890"
        self.code = "1234"
        self.user = User.objects.create(phone=self.phone, code=self.code)

    def test_verify_code_success(self):
        url = reverse('users:verify_code')
        data = {
            "phone": self.phone,
            "code": self.code,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)
        self.assertEqual(response.data["message"], "Авторизация успешна")

    def test_verify_code_invalid(self):
        url = reverse('users:verify_code')
        data = {
            "phone": self.phone,
            "code": "invalid_code",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["message"], "Неверный код или срок действия истек")

    def test_verify_code_user_not_found(self):
        url = reverse('users:verify_code')
        data = {
            "phone": "non_existent_phone",
            "code": "1234",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["message"], "Пользователь с таким номером телефона не найден")

    def test_verify_code_validation_error(self):
        url = reverse('users:verify_code')
        data = {
            "phone": self.phone,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("code", response.data)


class UserProfileViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create(phone="+79991234567")
        self.client.force_authenticate(user=self.user)

    def test_get_user_profile(self):
        url = reverse("users:user_profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["phone"], self.user.phone)


class PhoneLoginViewTestCase(APITestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("main:phone_login")

    def test_phone_login_view(self):
        response = self.client.post(self.url, {"phone": "+79991234567"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session["phone"], "+79991234567")

    @patch('users.services.send_sms')
    def test_post_sms_sending_failure(self, mock_send_sms):
        mock_send_sms.side_effect = Exception("Ошибка отправки SMS")

        response = self.client.post(self.url, {'phone': '+71234567890'})
        self.assertEqual(response.status_code, 302)
        self.assertContains(response, "Ошибка отправки SMS")


# class PhoneConfirmViewTestCase(APITestCase):
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create(phone="+79991234567")
#         self.code = self.user.generate_code()
#         session = self.client.session
#         session["phone"] = self.user.phone
#         session.save()
#         self.url = reverse("main:phone_confirm")
#
#     def test_phone_confirm_view_success(self):
#         response = self.client.post(self.url, {"code": self.code})
#         self.assertEqual(response.status_code, 302)
#
#     def test_phone_confirm_view_invalide_code(self):
#         response = self.client.post(self.url, {"code": "999999"})
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "Неверный код")
#
# class PhoneBackendTest(TestCase):
#
#     def setUp(self):
#         """Создаем пользователя для тестов"""
#         self.user = User.objects.create(phone="+79991234567")
#         # Генерация кода для пользователя
#         self.code = self.user.generate_code()
#
#     @patch("users.models.User.objects.get")
#     def test_authenticate_success(self, mock_get_user):
#         """Тест на успешную аутентификацию пользователя по телефону и коду"""
#         mock_get_user.return_value = self.user
#
#         backend = PhoneBackend()
#         authenticated_user = backend.authenticate(
#             None, phone="+79991234567", code=self.code
#         )
#
#         self.assertEqual(authenticated_user, self.user)
#         mock_get_user.assert_called_once_with(phone="+79991234567")
#
#     @patch("users.models.User.objects.get")
#     def test_authenticate_user_not_found(self, mock_get_user):
#         """Тест, если пользователь с таким телефоном не найден"""
#         mock_get_user.side_effect = User.DoesNotExist
#
#         backend = PhoneBackend()
#         authenticated_user = backend.authenticate(
#             None, phone="+79991234567", code=self.code
#         )
#
#         self.assertIsNone(authenticated_user)
#
#     @patch("users.models.User.objects.get")
#     def test_get_user_success(self, mock_get_user):
#         """Тест на получение пользователя по id"""
#         mock_get_user.return_value = self.user
#
#         backend = PhoneBackend()
#         user = backend.get_user(self.user.id)
#
#         self.assertEqual(user, self.user)
#         mock_get_user.assert_called_once_with(pk=self.user.id)
#
#     @patch("users.models.User.objects.get")
#     def test_get_user_not_found(self, mock_get_user):
#         """Тест, если пользователь не найден по id"""
#         mock_get_user.side_effect = User.DoesNotExist
#
#         backend = PhoneBackend()
#         user = backend.get_user(self.user.id)
#
#         self.assertIsNone(user)

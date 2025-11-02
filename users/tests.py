import string
import unittest
from unittest import TestCase
from unittest.mock import Mock, patch

import requests
from django.test import Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.backends import PhoneBackend
from users.models import User
from users.services import generate_invaite_code, send_sms


class RegisterViewTestCase(APITestCase):
    def test_register_new_user(self):
        url = reverse("users:register")
        data = {"phone": "+79991234567"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.filter(phone=data["phone"]).exists())
        self.assertEqual(response.data["message"], "Код отправлен")
        self.assertEqual(User.objects.count(), 1)

    def test_register_existing_user(self):
        user = User.objects.create(phone="+79991234567")
        url = reverse("users:register")
        data = {"phone": user.phone}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.filter(phone=data["phone"]).exists())
        self.assertEqual(response.data["message"], "Код отправлен")
        self.assertEqual(User.objects.count(), 1)

    def test_register_with_invaite_code(self):
        invaiter = User.objects.create(phone="+79991112233", invaite_code="INV123")
        url = reverse("users:register")
        data = {"phone": "+79991234567", "invaited_by": "INV123"}
        response = self.client.post(url, data)
        new_user = User.objects.get(phone=data["phone"])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(new_user.invaited_by, invaiter)
        self.assertEqual(response.data["message"], "Код отправлен")
        self.assertEqual(User.objects.count(), 2)

    def test_register_with_existing_invaite_code(self):
        invaiter = User.objects.create(phone="+79991112233", invaite_code="INV123")
        user = User.objects.create(phone="+79991234567", invaited_by=invaiter)
        url = reverse("users:register")
        data = {"phone": user.phone, "invaited_by": "NEWCODE"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("invaited_by", response.data)
        self.assertEqual(User.objects.count(), 2)

    # class VerifyCodeViewTestCase(APITestCase):
    #     def test_verify_correct_code(self):
    #         user = User.objects.create(phone="+79991234560")
    #         code = user.generate_code()
    #         url = reverse("users:verify_code")
    #         data = {"phone": user.phone, "code": code}
    #         response = self.client.post(url, data)
    #         self.assertEqual(response.status_code, status.HTTP_200_OK)
    #         self.assertIn("access", response.data)
    #         self.assertIn("refresh", response.data)

    def test_verify_wrong_code(self):
        user = User.objects.create(phone="+79991234567")
        url = reverse("users:verify_code")
        data = {"phone": user.phone, "code": "9999"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["message"], "Неверный код или срок действия истек"
        )
        self.assertEqual(User.objects.count(), 1)


class UserProfileViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(phone="+79991234567")
        self.client.force_authenticate(user=self.user)

    def test_get_user_profile(self):
        url = reverse("users:user_profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["phone"], self.user.phone)
        self.assertEqual(User.objects.count(), 1)


class PhoneLoginViewTestCase(APITestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("main:phone_login")

    def test_phone_login_view(self):
        response = self.client.post(self.url, {"phone": "+79991234567"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session["phone"], "+79991234567")
        self.assertEqual(User.objects.count(), 1)


class PhoneConfirmViewTestCase(APITestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(phone="+79991234567")
        self.code = self.user.generate_code()
        session = self.client.session
        session["phone"] = self.user.phone
        session.save()
        self.url = reverse("main:phone_confirm")

    def test_phone_confirm_view_success(self):
        response = self.client.post(self.url, {"code": self.code})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session["phone"], "+79991234567")
        self.assertEqual(User.objects.count(), 1)


class PhoneBackendTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(phone="+79991234567")
        self.code = self.user.generate_code()

    @patch("users.models.User.objects.get")
    def test_authenticate_user_not_found(self, mock_get_user):
        """Тест, если пользователь с таким телефоном не найден"""
        mock_get_user.side_effect = User.DoesNotExist

        backend = PhoneBackend()
        authenticated_user = backend.authenticate(None, phone="+799912", code=self.code)
        self.assertIsNone(authenticated_user)


class TestMyFunctions(unittest.TestCase):

    def test_generate_invite_code(self):
        code = generate_invaite_code()
        self.assertEqual(len(code), 6)
        self.assertTrue(all(c in string.ascii_uppercase + string.digits for c in code))

    @patch("requests.get")
    def test_send_sms_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_get.return_value = mock_response

        result = send_sms("+79991234567", "Ваш код: 1234")
        self.assertTrue(result)

    @patch("requests.get")
    def test_send_sms_failure(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Ошибка"
        mock_get.return_value = mock_response

        result = send_sms("+79991234567", "Ваш код: 1234")
        self.assertTrue(result)

    @patch("requests.get")
    def test_send_sms_network_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Ошибка сети")

        result = send_sms("+79991234567", "Ваш код: 123456")
        self.assertTrue(result)

    @patch("requests.get")
    def test_send_sms_unknown_error(self, mock_get):
        mock_get.side_effect = Exception("Неизвестная ошибка")

        result = send_sms("+79991234567", "Ваш код: 123456")
        self.assertTrue(result)

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from smsaero import SmsAeroException

from users.models import User
from unittest.mock import patch


class RegisterViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("users:register")

    def test_register_user_success(self):
        data = {
            "phone": "+1234567890",
            "invaite_code": "123qwe"
        }
        with patch('users.services.send_sms') as mock_send_sms:
            mock_send_sms.return_value = True
            response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Код отправлен")
        self.assertTrue(User.objects.filter(phone="+1234567890").exists())

    def test_register_user_with_invaition_code(self):
        invaited_user = User.objects.create(phone="+777777777", invaite_code="qwe123")

        data = {
            "phone": "+6666666666",
            "invaite_code": "123456",
        }

        with patch('users.services.send_sms') as mock_send_sms:
            mock_send_sms.return_value = True
            response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Код отправлен")
        user = User.objects.get(phone="+6666666666", invaite_code="123456", invaited_by="+777777777")
        self.assertEqual(user.invaited_by, invaited_user)

    def test_register_user_already_exists(self):
        User.objects.create(phone="+0987654321")

        data = {
            "phone": "+1234567890",
            "invaited_by": "123qwe",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("invaited_by", response.data)

    def test_register_user_invitation_code_already_set(self):
        user = User.objects.create(phone="+1234567890", invaite_code="123qwe",
                                   invaited_by=User.objects.create(phone="+6666666666"))

        data = {
            "phone": "+1234567890",
            "invaited_by": "123qwe123",
        }
        with patch('users.services.send_sms') as mock_send_sms:
            mock_send_sms.return_value = False
            response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("invaited_by", response.data)

    def test_register_user_sms_sending_error(self):
        data = {
            "phone": "+79961734335",
            "invaite_code": "123456aaa",

        }

        with patch('users.services.send_sms') as mock_send_sms:
            mock_send_sms.side_effect = SmsAeroException
            response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['message'], "Ошибка отправки SMS. Попробуйте позже.")

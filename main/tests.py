from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from users.models import User


class ProfileViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            phone="testuser", invaite_code="VALIDC", invaited_by=None
        )
        self.client.login(phone="testuser")
        self.url = reverse("main:profile")

    def test_get_context_data(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_post_invalid_invaite_code(self):
        response = self.client.post(self.url, {"invaite_code": "INVALIDCODE"})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 0)

    def test_post_already_used_invaite_code(self):
        invaiter = User.objects.create(phone="invaiter", invaite_code="VALIDCODE")
        self.user.invaited_by = invaiter
        self.user.save()

        response = self.client.post(self.url, {"invaite_code": "VALIDCODE"})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 0)

    def test_post_own_invaite_code(self):
        self.user.invaite_code = "MYOWNCODE"
        self.user.save()

        response = self.client.post(self.url, {"invaite_code": "MYOWNCODE"})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 0)

    def test_post_empty_invaite_code(self):
        response = self.client.post(self.url, {"invaite_code": ""})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 0)

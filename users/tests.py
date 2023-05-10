from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User


class UserRegistrationTest(APITestCase):
    def test_registration(self):
        url = reverse("user_view")
        user_data = {
            "email":"one@gmail.com",
            "password":"1",
            "username":"one",
            "gender":"F",
            "date_of_birth":"2001-01-01",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 201)


class UserLoginTest(APITestCase):
    def setUp(self):

        self.data = {
            "email":"one@gmail.com",
            "password":"1",
        }
        self.user = User.objects.create_user("one@gmail.com", "one", "1")
        return super().setUp()

    def test_login(self):
        url = reverse("token_obtain_pair")
        response = self.client.post(url, self.data)
        self.assertEqual(response.status_code, 200)
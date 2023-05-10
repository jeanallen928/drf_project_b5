from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


class UserRegistrationAPIViewTestCase(APITestCase):
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
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from users.serializers import UserProfileSerializer

from django.test.client import MULTIPART_CONTENT, encode_multipart, BOUNDARY
from PIL import Image
import tempfile


def get_temporary_image(temp_file):
    size = (200, 200)
    color = (255, 0, 0, 0)
    image = Image.new("RGBA", size, color)
    image.save(temp_file, "png")
    return temp_file


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


class UserProfileTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {"email": "one@gmail.com", "password": "1"}
        cls.profile_data = {
            "email": "one@gmail.com",
            "password": "1",
            "username": "one", 
            "gender": "F",
            "date_of_birth": "2001-01-01"
            }
        cls.user = User.objects.create_user("one@gmail.com", "one", "1")
        cls.users = []
        cls.users.append(User.objects.create_user("six@gmail.com", "six", "1"))
        cls.users.append(User.objects.create_user("two@gmail.com", "two", "1"))
        cls.users.append(User.objects.create_user("three@gmail.com", "three", "1"))
        cls.users.append(User.objects.create_user("four@gmail.com", "뽀", "1"))
        cls.users.append(User.objects.create_user("five@gmail.com", "five", "1"))


    def setUp(self):
        self.access_token = self.client.post(reverse("token_obtain_pair"), self.user_data).data["access"]
        
    
    def test_update_profile_with_image(self):
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.name = "image.png"
        image_file = get_temporary_image(temp_file)
        image_file.seek(0)

        self.profile_data["image"] = image_file

        response = self.client.put(
            path=reverse("myprofile_view"),
            data=encode_multipart(data=self.profile_data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )

        self.assertEqual(response.status_code, 200)


    def test_get_profile(self):
        for user in self.users:
            url = f"/user/profile/{user.id}/"
            response = self.client.get(url)
            serializer = UserProfileSerializer(user).data
            for key, value in serializer.items():
                self.assertEqual(response.data[key], value)

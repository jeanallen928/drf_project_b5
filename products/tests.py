from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from faker import Faker
from products.models import Product
from products.serializers import ProductSerializer, ProductCreateSerializer, ProductListSerializer, ProductReviewSerializer, ProductReviewCreateSerializer

# 이미지 업로드
from django.test.client import MULTIPART_CONTENT, encode_multipart, BOUNDARY
from PIL import Image
import tempfile

def get_temporary_image(temp_file):
    size = (200, 200)
    color = (255, 0, 0, 0)
    image = Image.new("RGBA", size, color)
    image.save(temp_file,'png')
    return temp_file

class ProductCreateTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser('admin@naver.com','admin_joonyeol','password')
        cls.admin_data = {'email':'admin@naver.com','password':'password'}
        cls.user = User.objects.create_user('test@naver.com','test_joonyeol','password')
        cls.user_data = {'email':'test@naver.com','password':'password'}
        cls.product_data = {'name':'product test name','introdution':'product test introduction','brand':'product test brand'}

    # admin, user의 access token을 받아옴
    def setUp(self):
        self.admin_access_token = self.client.post(reverse('token_obtain_pair'), self.admin_data).data['access']
        self.user_access_token = self.client.post(reverse('token_obtain_pair'), self.user_data).data['access']

    # 로그인 없이 post요청 보내면 401 확인
    def test_fail_if_not_logged_in(self):
        url = reverse("product_list")
        response = self.client.post(url, self.product_data)
        self.assertEqual(response.status_code, 401)

    # 로그인해도 admin이 아니면 403 확인
    def test_fail_if_not_admin(self):
        response = self.client.post(
            path=reverse("product_list"),
            data=self.product_data,
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            )
        self.assertEqual(response.status_code, 403)

    # admin이면 product 생성 확인
    def test_create_product(self):
        response = self.client.post(
            path=reverse("product_list"),
            data=self.product_data,
            HTTP_AUTHORIZATION=f"Bearer {self.admin_access_token}",
            )
        self.assertEqual(response.status_code, 201)

    # image 업로드 되는지 확인
    def test_create_product_with_image(self):
        # 임시 image 생성
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.name = "image.png"
        image_file = get_temporary_image(temp_file)
        image_file.seek(0)
        self.product_data["image"] = image_file

        # image response
        response = self.client.post(
            path=reverse("product_list"),
            data=encode_multipart(data = self.product_data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            HTTP_AUTHORIZATION=f"Bearer {self.admin_access_token}"
        )
        self.assertEqual(response.status_code, 201)


class ProductReadTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Faker를 사용해서 10개의 랜덤 product를 만듦
        cls.faker = Faker()
        cls.products = []
        for i in range(10):
            cls.products.append(Product.objects.create(name=cls.faker.sentence(), introdution=cls.faker.text()))

    # 랜덤 생성한 product의 response와 serializer의 값이 같은지 확인
    def test_get_product(self):
        for product in self.products:
            url = product.get_absolute_url()
            response = self.client.get(url)
            serializer = ProductSerializer(product).data
            for key, value in serializer.items():
                self.assertEqual(response.data[key], value)

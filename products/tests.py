from rest_framework.test import APITestCase, APIClient
from users.models import CustomUser as User
from django.contrib.auth.models import Group
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image
import os
from .models import Product, Category


class ProductListTests(APITestCase):
    def setUp(self):
        self.url = reverse("product-list-create")
        self.user = User.objects.create_user(username="testuser", password="userpass")
        self.client = APIClient()

        self.image = Image.new("RGB", (100, 100)).save("test.jpeg", "jpeg")
        self.category = Category.objects.create(name="TestCategory")

        self.product_data = {
            "added_by": self.user,
            "name": "Product 1",
            "description": "Description 1",
            "price": 10.00,
            "stock": 5,
            "images": self.image,
            "label": "SALE",
            "category": self.category,
        }

    def test_login(self):
        url = reverse("jwt-create")
        data = {"username": "testuser", "password": "userpass"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.access_token = response.data["access"]

    def test_list_create_products(self):
        # Product.objects.create(**self.product_data)
        url = reverse("product-list-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

        self.test_login()
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data["name"], "Product 1")
        self.assertEqual(len(response.data), 1)


# class ProductDetailTests(APITestCase):

#     def setUp(self):
#         self.user = User.objects.create(username="testuser", password="userpass")

#         manager_group = Group.objects.create(name="Manager")
#         self.manager = User.objects.create(username="manager", password="managerpass")
#         self.manager.groups.add(manager_group)

#     # def test_product_detail(self):
#     #     response = self.client.get("/api/products/1/")
#     #     self.assertEqual(response.status_code, 200)

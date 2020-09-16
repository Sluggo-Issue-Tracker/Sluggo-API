from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from dj_rest_auth import urls

User = get_user_model()

user_dict = {
    "username": "sschmidt",
    "password1": "p@ssw0rd90",
    "password2": "p@ssw0rd90",
    "email": "sadschmi@ucsc.edu"
}


class AuthenticationBaseBehavior(TestCase):

    def setUp(self):
        self.client = APIClient()

    def testShit(self):
        response = self.client.post(
           reverse('rest_register'), user_dict
        )

        print(response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

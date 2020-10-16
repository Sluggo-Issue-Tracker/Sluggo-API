from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from dj_rest_auth import urls

User = get_user_model()


class AuthenticationBaseBehavior(TestCase):

    def setUp(self):
        self.client = APIClient()

        response = self.client.post(
            reverse('rest_register'),
            {
                "username": "sschmidt",
                "password1": "p@ssw0rd90",
                "password2": "p@ssw0rd90",
                "email": "sadschmi@test.com"
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertGreater(User.objects.count(), 0)

    def testRegister(self):

        response = self.client.post(
            reverse('rest_login'),
            {
                'username': 'sschmidt',
                'email': 'sadschmi@test.com',
                'password': 'p@ssw0rd90'
            }
        )

        print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testLogout(self):

        response = self.client.post(
            reverse('rest_login'),
            {
                'username': 'sschmidt',
                'email': 'sadschmi@test.com',
                'password': 'p@ssw0rd90'
            }
        )

        print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            reverse('rest_logout')
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)



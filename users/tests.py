from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

User = get_user_model()


class AuthTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.token_url = reverse('token_obtain_pair')
        self.test_user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'strongpassword123'
        }

    def test_register_user(self):
        response = self.client.post(self.register_url, self.test_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.json())
        self.assertIn('refresh', response.json())
        self.assertEqual(response.json()['user']['username'], self.test_user_data['username'])

    def test_user_login(self):
        self.client.post(self.register_url, self.test_user_data, format='json')
        login_data = {
            'username': self.test_user_data['username'],
            'password': self.test_user_data['password'],
        }

        response = self.client.post(self.token_url, self.test_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.json())
        self.assertIn('refresh', response.json())

    def test_access_protected_endpoint_without_auth(self):
        protected_url = reverse('habit-list')
        response = self.client.get(protected_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_protected_endpoint_with_auth(self):
        self.client.post(self.register_url, self.test_user_data, format='json')
        login_data = {
            'username': self.test_user_data['username'],
            'password': self.test_user_data['password'],
        }
        token_response = self.client.post(self.token_url, self.test_user_data, format='json')
        access_token = token_response.json()['access']

        protected_url = reverse('habit-list')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(protected_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from habits.models import Habit

User = get_user_model()


class HabitAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1_password = 'pass1234'
        self.user2_password = 'pass5678'
        self.user1 = User.objects.create_user(username='user1', password=self.user1_password)
        self.user2 = User.objects.create_user(username='user2', password=self.user2_password)

        self.token_url = reverse('token_obtain_pair')

        self.habit_user1 = Habit.objects.create(user=self.user1, name='Run every day')
        self.habit_data = {
            'name': 'Read books',
            'description': 'Read 30 pages',
            'start_date': '2025-06-03',
            'is_active': True,
        }

    def authenticate_user(self, username, password):
        response = self.client.post(self.token_url, {'username': username, 'password': password}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.json()['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}' )

    def test_get_own_habits(self):
        self.authenticate_user(self.user1.username, self.user1_password)
        url = reverse('habit-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['name'], self.habit_user1.name)

    def test_cannot_access_other_users_habit(self):
        self.authenticate_user(self.user2.username, self.user2_password)
        url = reverse('habit-detail', args=[self.habit_user1.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_habit(self):
        self.authenticate_user(self.user1.username, self.user1_password)
        url = reverse('habit-list')
        response = self.client.post(url, data=self.habit_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['name'], self.habit_data['name'])
        self.assertEqual(response.json()['user'], self.user1.id)

    def test_update_habit(self):
        self.authenticate_user(self.user1.username, self.user1_password)
        url = reverse('habit-detail', args=[self.habit_user1.id])
        updated_data = {'name': 'Run every morning'}
        response = self.client.patch(url, data=updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], updated_data['name'])

    def test_delete_habits(self):
        self.authenticate_user(self.user1.username, self.user1_password)
        url = reverse('habit-detail', args=[self.habit_user1.id])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Habit.objects.filter(id=self.habit_user1.id).exists())

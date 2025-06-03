from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from habits.models import Habit, HabitSchedule, HabitRecord

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


class HabitScheduleAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='pass1234')
        self.token_url = reverse('token_obtain_pair')

        self.habit = Habit.objects.create(user=self.user, name='Workout')

        self.schedule_data = {
            'day_of_week': 0
        }

    def authenticate(self):
        response = self.client.post(self.token_url, {'username': 'user', 'password': 'pass1234'}, format='json')
        token = response.json()['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_list_schedule(self):
        self.authenticate()
        HabitSchedule.objects.create(habit=self.habit, day_of_week=1)
        url = reverse('habit-schedule-list', args=[self.habit.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['day_of_week'], 1)

    def test_create_schedule(self):
        self.authenticate()
        url = reverse('habit-schedule-list', args=[self.habit.id])
        response = self.client.post(url, data=self.schedule_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['day_of_week'], self.schedule_data['day_of_week'])

    def test_cannot_create_schedule_for_other_users_habit(self):
        other_user = User.objects.create_user(username='other', password='pass5678')
        other_habit = Habit.objects.create(user=other_user, name='Read')
        self.authenticate()
        url = reverse('habit-schedule-list', args=[other_habit.id])
        response = self.client.post(url, self.schedule_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)



from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django_celery_beat.models import PeriodicTask
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from habits.models import Habit, HabitRecord, HabitSchedule
from habits.utils import create_or_update_task_for_schedule

User = get_user_model()


class HabitAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1_password = "pass1234"
        self.user2_password = "pass5678"
        self.user1 = User.objects.create_user(username="user1", password=self.user1_password)
        self.user2 = User.objects.create_user(username="user2", password=self.user2_password)

        self.token_url = reverse("token_obtain_pair")

        self.habit_user1 = Habit.objects.create(user=self.user1, name="Run every day")
        self.habit_data = {
            "name": "Read books",
            "description": "Read 30 pages",
            "start_date": "2025-06-03",
            "is_active": True,
        }

    def authenticate_user(self, username, password):
        response = self.client.post(self.token_url, {"username": username, "password": password}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.json()["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_get_own_habits(self):
        self.authenticate_user(self.user1.username, self.user1_password)
        url = reverse("habit-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["name"], self.habit_user1.name)

    def test_cannot_access_other_users_habit(self):
        self.authenticate_user(self.user2.username, self.user2_password)
        url = reverse("habit-detail", args=[self.habit_user1.id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_habit(self):
        self.authenticate_user(self.user1.username, self.user1_password)
        url = reverse("habit-list")
        response = self.client.post(url, data=self.habit_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["name"], self.habit_data["name"])
        self.assertEqual(response.json()["user"], self.user1.id)

    def test_update_habit(self):
        self.authenticate_user(self.user1.username, self.user1_password)
        url = reverse("habit-detail", args=[self.habit_user1.id])
        updated_data = {"name": "Run every morning"}
        response = self.client.patch(url, data=updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["name"], updated_data["name"])

    def test_delete_habits(self):
        self.authenticate_user(self.user1.username, self.user1_password)
        url = reverse("habit-detail", args=[self.habit_user1.id])
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Habit.objects.filter(id=self.habit_user1.id).exists())


class HabitScheduleAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass1234")
        self.token_url = reverse("token_obtain_pair")

        self.habit = Habit.objects.create(user=self.user, name="Workout")

        self.schedule_data = {"day_of_week": 0}

    def authenticate(self):
        response = self.client.post(self.token_url, {"username": "user", "password": "pass1234"}, format="json")
        token = response.json()["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_list_schedule(self):
        self.authenticate()
        HabitSchedule.objects.create(habit=self.habit, day_of_week=1)
        url = reverse("habit-schedule-list", args=[self.habit.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["day_of_week"], 1)

    def test_create_schedule(self):
        self.authenticate()
        url = reverse("habit-schedule-list", args=[self.habit.id])
        response = self.client.post(url, data=self.schedule_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["day_of_week"], self.schedule_data["day_of_week"])

    def test_cannot_create_schedule_for_other_users_habit(self):
        other_user = User.objects.create_user(username="other", password="pass5678")
        other_habit = Habit.objects.create(user=other_user, name="Read")
        self.authenticate()
        url = reverse("habit-schedule-list", args=[other_habit.id])
        response = self.client.post(url, self.schedule_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class HabitRecordAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass1234")
        self.token_url = reverse("token_obtain_pair")

        self.habit = Habit.objects.create(user=self.user, name="Meditate")

        self.record_data = {
            "date": str(date.today()),
            "completed": True,
        }

    def authenticate(self):
        response = self.client.post(self.token_url, {"username": "user", "password": "pass1234"}, format="json")
        token = response.json()["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_create_record(self):
        self.authenticate()
        url = reverse("habit-records-list", args=[self.habit.id])
        response = self.client.post(url, self.record_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["completed"], self.record_data["completed"])

    def test_list_records(self):
        self.authenticate()
        HabitRecord.objects.create(habit=self.habit, date=date.today(), completed=True)
        url = reverse("habit-records-list", args=[self.habit.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_cannot_create_record_for_other_users_habit(self):
        other_user = User.objects.create_user(username="other", password="pass5678")
        other_habit = Habit.objects.create(user=other_user, name="Read")
        self.authenticate()
        url = reverse("habit-records-list", args=[other_habit.id])
        response = self.client.post(url, self.record_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class HabitScheduleAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")
        self.habit = Habit.objects.create(user=self.user, name="Test habit")

    def tearDown(self):
        PeriodicTask.objects.all().delete()

    def authenticate(self):
        self.token_url = reverse("token_obtain_pair")
        response = self.client.post(self.token_url, {"username": "testuser", "password": "testpass"}, format="json")
        token = response.json().get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_create_habit_schedule_creates_periodictask(self):
        self.authenticate()

        url = reverse("habit-schedule-list", kwargs={"habit_pk": self.habit.id})
        data = {"habit": self.habit.id, "day_of_week": 0, "remind_hour": 9, "remind_minute": 0}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        schedule_id = response.data["id"]
        schedule = HabitSchedule.objects.get(id=schedule_id)

        create_or_update_task_for_schedule(schedule)

        task_name = f"remind_habit_{schedule_id}"
        self.assertTrue(PeriodicTask.objects.filter(name=task_name).exists())

    def test_update_habit_schedule_updates_periodictask(self):
        self.authenticate()

        schedule = HabitSchedule.objects.create(habit=self.habit, day_of_week=2, remind_hour=9, remind_minute=30)
        create_or_update_task_for_schedule(schedule)

        schedule.remind_hour = 10
        schedule.remind_minute = 15
        schedule.save()

        create_or_update_task_for_schedule(schedule)

        task_name = f"remind_habit_{schedule.id}"
        task = PeriodicTask.objects.get(name=task_name)
        crontab = task.crontab

        self.assertEqual(task.task, "habits.task.send_habit_email")
        self.assertEqual(crontab.hour, str(10))
        self.assertEqual(crontab.minute, str(15))

    def test_delete_habit_schedule_deletes_periodictask(self):
        self.authenticate()

        schedule = HabitSchedule.objects.create(habit=self.habit, day_of_week=0, remind_hour=7, remind_minute=0)
        create_or_update_task_for_schedule(schedule)

        task_name = f"remind_habit_{schedule.id}"
        self.assertTrue(PeriodicTask.objects.filter(name=task_name).exists())

        url = reverse("habit-schedule-detail", kwargs={"habit_pk": self.habit.id, "pk": schedule.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(PeriodicTask.objects.filter(name=task_name).exists())


class HabitAnalyticsViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

        self.habit = Habit.objects.create(name='Test Habit', user=self.user)

        today = date.today()
        HabitRecord.objects.create(habit=self.habit, date=today, completed=True)
        HabitRecord.objects.create(habit=self.habit, date=today - timedelta(days=1), completed=True)
        HabitRecord.objects.create(habit=self.habit, date=today - timedelta(days=2), completed=False)  # не считается

        self.other_user = User.objects.create_user(username='otheruser', password='password')
        self.other_habit = Habit.objects.create(name='Other Habit', user=self.other_user)
        HabitRecord.objects.create(habit=self.other_habit, date=today, completed=True)

    def authenticate(self, username, password):
        self.token_url = reverse("token_obtain_pair")
        response = self.client.post(self.token_url, {"username": username, "password": password}, format="json")
        token = response.json().get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_analytics_basic(self):
        self.authenticate(self.user.username, 'password')

        url = reverse('habit-analytics', kwargs={'habit_pk': self.habit.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        dates = [item['date'] for item in response.data]
        self.assertIn(date.today(), dates)
        self.assertIn(date.today() - timedelta(days=1), dates)
        self.assertNotIn(date.today() - timedelta(days=2), dates)

        for item in response.data:
            self.assertEqual(item['completed_count'], 1)

    def test_analytics_filter_by_date(self):
        self.authenticate(self.user.username, 'password')
        url = reverse('habit-analytics', kwargs={'habit_pk': self.habit.pk})

        start_date = date.today() - timedelta(days=1)
        response = self.client.get(url, {'start_date': start_date})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data:
            self.assertGreaterEqual(item['date'], start_date)

        end_date = date.today() - timedelta(days=1)
        response = self.client.get(url, {'end_date': end_date})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data:
            self.assertLessEqual(item['date'], end_date)

    def test_analytics_reject_other_habit(self):
        self.authenticate(self.user.username, 'password')

        url = reverse('habit-analytics', kwargs={'habit_pk': self.other_habit.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

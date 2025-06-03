from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Habit(models.Model):
    """
    Represents the habit the user wants to track.
    Contains basic information about the habit: user, name, description,
    start_date, is_active, created_at
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    start_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} ({self.user.username})'


class HabitSchedule(models.Model):
    """
    Determines which days of the week the user plans to perform the habit.
    One day of the week can be linked to one habit only once.
    """

    DAYS_OF_WEEK = [
        (0, 'Понеділок'),
        (1, 'Вівторок'),
        (2, 'Середа'),
        (3, 'Четвер'),
        (4, 'П\'ятниця'),
        (5, 'Субота'),
        (6, 'Неділя'),
    ]

    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='schedule')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)

    class Meta:
        unique_together = ('habit', 'day_of_week')

    def __str__(self):
        return f'{self.habit.name} — {self.get_day_of_week_display()}'


class HabitRecord(models.Model):
    """
    Indicates whether the habit was performed on a specific date and
    when exactly it was completed.
    """

    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='records')
    date = models.DateField()
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('habit', 'date')

    def __str__(self):
        return f'{self.habit.name} — {self.date} — {"Готово" if self.completed else "Не завершено"}'

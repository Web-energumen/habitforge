import json

from django.conf import settings
from django_celery_beat.models import CrontabSchedule, PeriodicTask


def create_or_update_task_for_schedule(habit_schedule):
    hour = habit_schedule.remind_hour
    minute = habit_schedule.remind_minute

    # У моделі HabitSchedule 0 - це понеділок, а в Crontab 0 - це неділя,
    # тому потрібно змістити дні тижня на 1 вправо, щоб перевести день тижня у формат,
    # зрозумілий crontab.Наприклад: якщо habit_schedule.day_of_week == 0 (Понеділок),
    # то day_map[0] поверне '1' - Понеділок для crontab.
    day_map = {0: "1", 1: "2", 2: "3", 3: "4", 4: "5", 5: "6", 6: "0"}
    day_of_week = day_map[habit_schedule.day_of_week]

    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute=str(minute),
        hour=str(hour),
        day_of_week=day_of_week,  # тільки в потрібний день тижня
        day_of_month="*",  # тільки в потрібний день тижня# у будь-який день місяця
        month_of_year="*",  # у будь-який місяць
        timezone=settings.TIME_ZONE,
    )

    task_name = f"remind_habit_{habit_schedule.id}"
    task_args = json.dumps([habit_schedule.habit.user.id, habit_schedule.habit.id])

    PeriodicTask.objects.update_or_create(
        name=task_name,
        defaults={
            "crontab": schedule,
            "task": "habits.task.send_habit_email",
            "args": task_args,
            "enabled": habit_schedule.habit.is_active,
        },
    )

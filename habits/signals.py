from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask

from .models import HabitSchedule
from .utils import create_or_update_task_for_schedule


@receiver(post_save, sender=HabitSchedule)
def habit_schedule_save(sender, instance, **kwargs):
    create_or_update_task_for_schedule(instance)


@receiver(post_delete, sender=HabitSchedule)
def habit_schedule_delete(sender, instance, **kwargs):
    task_name = f"remind_habit_{instance.id}"
    PeriodicTask.objects.filter(name=task_name).delete()

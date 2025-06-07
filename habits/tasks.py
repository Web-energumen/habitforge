from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from .models import Habit


@shared_task
def send_habit_email(user_id, habit_id):
    User = get_user_model()
    try:
        user = User.objects.get(pk=user_id)
        habit = Habit.objects.get(pk=habit_id, user=user)
    except (User.DoesNotExist, Habit.DoesNotExist):
        return False

    send_mail(
        subject='Habit Tracker: Нагадування про звичку',
        message=f'Привіт {user.username}, не забудь виконати звичку: {habit.name}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=False,
    )

    return True

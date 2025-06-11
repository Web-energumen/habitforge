from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_email_verification(user_email, verification_link):
    subject = 'Habit Tracker: Підтвердження реєстрації'
    message = f'Перейдіть за посиланням для підтвердження: {verification_link}'

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user_email],
        fail_silently=False,
    )

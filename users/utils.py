from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def generate_email_verification_token(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    verify_url = reverse('verify-email', kwargs={'uidb64': uid, 'token': token})
    full_url = f'{settings.BASE_URL}{verify_url}'

    return full_url

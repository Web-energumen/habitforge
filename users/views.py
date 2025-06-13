from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer
from .tasks import send_email_verification
from .utils import generate_email_verification_token

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        verification_path = generate_email_verification_token(user)

        send_email_verification.delay(user.email, verification_path)

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": serializer.data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "detail": "Перевірте email для підтвердження реєстрації.",
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if not default_token_generator.check_token(user, token):
                return Response({"detail": "Невірний токен."}, status=status.HTTP_400_BAD_REQUEST)

            user.is_active = True
            user.save()

            return Response({"detail": "Обліковий запис успішно активовано."}, status=status.HTTP_200_OK)

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"detail": "Користувача не знайдено."}, status=status.HTTP_400_BAD_REQUEST)

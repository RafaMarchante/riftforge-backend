from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.authentication.tasks import send_verification_email, send_password_reset_email, send_password_change_confirmation_email
from apps.authentication.serializers import RegisterSerializer
from .auth_token_service import AuthTokenService

import logging
logger = logging.getLogger(__name__)


User = get_user_model()


class AuthService:
    @staticmethod
    def register_profile(data):
        serializer = RegisterSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        uid, token = AuthTokenService.generate_email_token(user)
        send_verification_email.delay(user.email, uid, token)

    @staticmethod
    def verify_email(uid, token):
        user = AuthTokenService.validate_email_token(uid, token)

        if not user:
            logger.warning("Invalid token attempt - uid: %s", uid)
            raise ValueError("Invalid token")

        if user.is_active:
            logger.info("Attempt to verify already verified email - uid: %s", uid)
            raise ValueError("Email already verified")

        user.is_active = True
        user.save()

    @staticmethod
    def resend_verification_email(email):
        user = User.objects.filter(email=email).first()

        if user and not user.is_active:
            uid, token = AuthTokenService.generate_email_token(user)
            send_verification_email.delay(user.email, uid, token)

    @staticmethod
    def request_password_reset(email):
        user = User.objects.filter(email=email).first()

        if user:
            uid, token = AuthTokenService.generate_email_token(user)
            send_password_reset_email.delay(user.email, uid, token)

    @staticmethod
    def confirm_password_reset(uid, token, new_password):
        if not new_password:
            raise ValueError("new_password is required")

        try:
            validate_password(new_password)
        except ValidationError:
            logger.warning("Invalid new password attempt - uid: %s", uid)
            raise ValueError("Invalid new password")

        user = AuthTokenService.validate_email_token(uid, token)

        if not user:
            logger.warning("Invalid token attempt - uid: %s", uid)
            raise ValueError("Invalid or expired token")

        user.set_password(new_password)
        user.save()

        send_password_change_confirmation_email.delay(user.email)

    @staticmethod
    def login(request, email, password):
        user = authenticate(request, email=email, password=password)

        if user is None or not user.is_active:
            logger.warning("Failed login attempt for email: %s", email)
            raise ValueError("Invalid credentials")

        update_last_login(None, user)

        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    @staticmethod
    def logout(refresh_token):
        if not refresh_token:
            raise ValueError("Refresh token required")
        try:
            RefreshToken(refresh_token).blacklist()
        except Exception:
            logger.error("Failed to blacklist refresh token")
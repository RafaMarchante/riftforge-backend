from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.authentication.tasks import send_password_change_confirmation_email, send_profile_deletion_email
from apps.users.serializers import UpdateProfileSerializer, UpdateAvatarSerializer

import logging
logger = logging.getLogger(__name__)


User = get_user_model()


class UserService:
    @staticmethod
    def update_profile(user, data):
        serializer = UpdateProfileSerializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    @staticmethod
    def update_avatar(user, data):
        old_avatar = user.avatar_image

        serializer = UpdateAvatarSerializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)

        if old_avatar and old_avatar.name != settings.DEFAULT_AVATAR:
            old_avatar.delete(save=False)

        serializer.save()
        return serializer.data

    @staticmethod
    def change_password(user, current_password, new_password):
        if not current_password or not new_password:
            raise ValueError("Both fields are required")

        if not user.check_password(current_password):
            raise ValueError("Current password is incorrect")

        try:
            validate_password(new_password, user=user)
        except ValidationError as e:
            logger.warning("Invalid new password for user: %s - %s", user.id, "; ".join(e.messages))
            raise ValueError("Invalid new password")

        user.set_password(new_password)
        user.save()

        send_password_change_confirmation_email.delay(user.email)

    @staticmethod
    def delete_profile(user, password, refresh_token):
        if not password or not refresh_token:
            raise ValueError("Password and refresh token are required")

        if not user.check_password(password):
            raise ValueError("Password is incorrect")

        try:
            RefreshToken(refresh_token).blacklist()
        except Exception:
            logger.error("Failed to blacklist refresh token for user: %s", user.id)
            raise ValueError("Invalid or expired token")

        email = user.email

        try:
            avatar = user.avatar_image
            if avatar and avatar.name != settings.DEFAULT_AVATAR:
                avatar.delete(save=False)
            user.delete()
        except Exception:
            logger.exception("Failed to delete profile for user: %s", user.id)
            raise

        send_profile_deletion_email.delay(email)
        logger.info("Profile deleted for user: %s", email)
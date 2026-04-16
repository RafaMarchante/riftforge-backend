from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
import datetime

class PasswordAwareJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)

        issued_at = validated_token.get("iat")
        if issued_at and user.password_changed_at:
            token_iat = datetime.datetime.fromtimestamp(issued_at, tz=datetime.timezone.utc)
            if token_iat < user.password_changed_at:
                raise InvalidToken("Token invalidated due to password change")

        return user
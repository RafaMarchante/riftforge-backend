from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

from .tasks import send_verification_email, send_password_reset_email
from .serializers import RegisterSerializer
from .services import AuthTokenService

import logging
logger = logging.getLogger(__name__)


User = get_user_model()


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        uid, token = AuthTokenService.generate_email_token(user)
        try:
            send_verification_email.delay(user.email, uid, token)
        except Exception:
            logger.error("Failed to send verification email for user: %s", user.id)
            return Response({"error": "Failed to send verification email"}, status=500)

        return Response({"message": "Check your email to verify account"})


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class VerifyEmailView(APIView):
    def post(self, request, uid, token):
        user = AuthTokenService.validate_email_token(uid, token)

        if not user:
            logger.warning("Invalid token attempt - uid: %s", uid)
            return Response({"error": "Invalid token"}, status=400)
        
        if user.is_active:
            logger.info("Attempt to verify already verified email - uid: %s", uid)
            return Response({"message": "Email already verified"})

        user.is_active = True
        user.save()

        return Response({"message": "Email verified"})


@method_decorator(ratelimit(key='ip', rate='3/m', method='POST', block=True), name='post')
class ResendVerificationEmailView(APIView):
    def post(self, request):
        email = request.data.get("email")
        user = User.objects.filter(email=email).first()

        if user and not user.is_active:
            uid, token = AuthTokenService.generate_email_token(user)
            try:
                send_verification_email.delay(user, uid, token)
            except Exception:
                logger.error("Failed to send verification email for user: %s", user.id)
                return Response({"error": "Failed to send verification email"}, status=500)

        return Response({"message": "If an unverified account exists, a verification email has been sent."})
    

@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get("email")
        user = User.objects.filter(email=email).first()

        if user:
            uid, token = AuthTokenService.generate_email_token(user)
            try:
                send_password_reset_email.delay(user, uid, token)
            except Exception:
                logger.error("Failed to send password reset email for user: %s", user.id)
                return Response({"error": "Failed to send password reset email"}, status=500)

        return Response({"message": "If an account exists, a reset email has been sent."})
    

@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class PasswordResetConfirmView(APIView):
    def post(self, request, uid, token):
        new_password = request.data.get("new_password")
        
        if not new_password:
            return Response({"error": "new_password is required"}, status=400)
        
        try:
            validate_password(new_password)
        except ValidationError:
            logger.warning("Invalid new password for user: %s", request.user.id)
            return Response({"error": "Invalid new password"}, status=400)

        user = AuthTokenService.validate_email_token(uid, token)

        if not user:
            logger.warning("Invalid token attempt - uid: %s", uid)
            return Response({"error": "Invalid or expired token"}, status=400)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password updated successfully"})


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, email=email, password=password)

        if user is None or not user.is_active:
            logger.warning("Failed login attempt for email: %s", email)
            return Response({"error": "Invalid credentials"}, status=401)

        update_last_login(None, user)

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        token = request.data.get("refresh")
        if not token:
            return Response({"error": "Refresh token required"}, status=400)
        try:
            RefreshToken(token).blacklist()
            return Response(status=205)
        except Exception:
            logger.error("Failed to blacklist refresh token")
            return Response({"error": "Invalid or expired token"}, status=400)

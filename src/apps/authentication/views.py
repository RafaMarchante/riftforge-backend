from django.contrib.auth import get_user_model
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .services.auth_service import AuthService

import logging
logger = logging.getLogger(__name__)


User = get_user_model()


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class RegisterProfileView(APIView):
    def post(self, request):
        try:
            AuthService.register_profile(request.data)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response({"error": "Failed to register profile"}, status=500)
        
        return Response({"message": "Check your email to verify account"})


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class VerifyEmailView(APIView):
    def post(self, request, uid, token):
        try:
            AuthService.verify_email(uid, token)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response({"error": "Failed to verify email"}, status=500)

        return Response({"message": "Email verified"})


@method_decorator(ratelimit(key='ip', rate='3/m', method='POST', block=True), name='post')
class ResendVerificationEmailView(APIView):
    def post(self, request):
        email = request.data.get("email")
        
        try:
            AuthService.resend_verification_email(email)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response({"error": "Failed to resend verification email"}, status=500)

        return Response({"message": "If an unverified account exists, a verification email has been sent."})
    

@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get("email")
        
        try:
            AuthService.request_password_reset(email)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response({"error": "Failed to request password reset"}, status=500)

        return Response({"message": "If an account exists, a reset email has been sent."})
    

@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class PasswordResetConfirmView(APIView):
    def post(self, request, uid, token):
        new_password = request.data.get("new_password")
        
        try:
            AuthService.confirm_password_reset(uid, token, new_password)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response({"error": "Failed to reset password"}, status=500)

        return Response({"message": "Password updated successfully"})


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            tokens = AuthService.login(request,email, password)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response({"error": "Failed to login"}, status=500)
        
        return Response(tokens)


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        refresh = request.data.get("refresh")
        
        try:
            AuthService.logout(refresh)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response({"error": "Failed to logout"}, status=500)
        
        return Response({"message": "Logged out successfully"})

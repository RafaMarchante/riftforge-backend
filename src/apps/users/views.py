from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from apps.authentication.tasks import send_profile_deletion_email
from .serializers import ProfileSerializer
from .services.user_service import UserService

import logging
logger = logging.getLogger(__name__)


User = get_user_model()


@method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True), name='get')
class GetProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user, context={'request': request})
        return Response(serializer.data)


@method_decorator(ratelimit(key='ip', rate='5/m', method='PATCH', block=True), name='patch')
class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        try:
            data = UserService.update_profile(request.user, request.data)
        except Exception:
            return Response({"error": "Failed to update profile"}, status=500)
        
        return Response(data)


@method_decorator(ratelimit(key='ip', rate='5/m', method='PATCH', block=True), name='patch')
class UpdateAvatarView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def patch(self, request):
        try:
            data = UserService.update_avatar(request.user, request.data)
        except Exception:
            return Response({"error": "Failed to update avatar"}, status=500)
        
        return Response(data)


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        try:
            UserService.change_password(request.user, current_password, new_password)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception:
            return Response({"error": "Failed to change password"}, status=500)

        return Response({"message": "Password changed successfully"})


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class DeleteProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        password = request.data.get("password")
        refresh = request.data.get("refresh")
        
        try:
            UserService.delete_profile(request.user, password, refresh)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception:
            return Response({"error": "Failed to delete profile"}, status=500)
        
        return Response({"message": "Profile deleted successfully"})
        
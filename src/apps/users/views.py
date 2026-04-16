from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated

from .serializers import UpdateProfileSerializer, UpdateAvatarSerializer

import logging
logger = logging.getLogger(__name__)


User = get_user_model()


@method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True), name='get')
class GetProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "email": user.email,
            "avatar_image": user.avatar_image.url if user.avatar_image else None,
            "last_login": user.last_login,
            "date_joined": user.date_joined
        })


@method_decorator(ratelimit(key='ip', rate='5/m', method='PATCH', block=True), name='patch')
class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@method_decorator(ratelimit(key='ip', rate='5/m', method='PATCH', block=True), name='patch')
class UpdateAvatarView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def patch(self, request):
        old_avatar = request.user.avatar_image
        
        serializer = UpdateAvatarSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        if old_avatar and old_avatar.name != 'images/default_avatar.png':
            old_avatar.delete(save=False)

        serializer.save()
        return Response(serializer.data)


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        if not current_password or not new_password:
            return Response({"error": "Both fields are required"}, status=400)

        if not request.user.check_password(current_password):
            return Response({"error": "Current password is incorrect"}, status=400)

        try:
            validate_password(new_password, user=request.user)
        except ValidationError as e:
            logger.warning("Invalid new password for user: %s", request.user.id)
            return Response({"error": "Invalid new password"}, status=400)

        request.user.set_password(new_password)
        request.user.save()

        return Response({"message": "Password changed successfully"})

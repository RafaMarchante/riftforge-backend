from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']

    def validate_username(self, value):
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError("Username already taken")
        return value


class UpdateAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['avatar_image']
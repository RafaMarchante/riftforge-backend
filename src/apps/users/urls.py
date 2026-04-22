from django.urls import path
from .views import GetProfileView, UpdateAvatarView, UpdateProfileView, ChangePasswordView, DeleteProfileView


urlpatterns = [
    path('profile', GetProfileView.as_view(), name='get_profile'),
    path('profile/update', UpdateProfileView.as_view(), name='update_profile'),
    path('profile/update/avatar', UpdateAvatarView.as_view(), name='update_avatar'),
    path('profile/change-password', ChangePasswordView.as_view(), name='change_password'),
    path('profile/delete', DeleteProfileView.as_view(), name='delete_profile'),
]

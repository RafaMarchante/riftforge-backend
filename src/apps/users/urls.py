from django.urls import path
from .views import GetProfileView, UpdateAvatarView, ChangePasswordView


urlpatterns = [
    path('profile/', GetProfileView.as_view(), name='get_profile'),
    path('profile/avatar/', UpdateAvatarView.as_view(), name='update_avatar'),
    path('profile/change-password/', ChangePasswordView.as_view(), name='change_password'),
]
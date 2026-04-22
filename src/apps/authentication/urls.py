from django.urls import path
from .views import (
    RegisterProfileView,
    VerifyEmailView,
    LoginView,
    LogoutView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    ResendVerificationEmailView)
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('register', RegisterProfileView.as_view(), name='register_profile'),
    path('verify-email/<uid>/<token>', VerifyEmailView.as_view(), name='verify_email'),
    path('resend-verification-email', ResendVerificationEmailView.as_view(), name='resend_verification_email'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('reset-password', PasswordResetRequestView.as_view(), name='reset_password'),
    path('reset-password-confirm/<uid>/<token>', PasswordResetConfirmView.as_view(), name='reset_password_confirm'),
]

from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse


def send_verification_email(user_email, uid, token):
    path = reverse('verify_email', kwargs={'uid': uid, 'token': token})
    url = f"{settings.BASE_URL}{path}"
    send_mail(
        subject="Verify your account",
        message=f"Click to verify: {url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
    )


def send_password_reset_email(user_email, uid, token):
    path = reverse('reset_password_confirm', kwargs={'uid': uid, 'token': token})
    url = f"{settings.BASE_URL}{path}"
    send_mail(
        subject="Reset your password",
        message=f"Click to reset your password: {url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
    )
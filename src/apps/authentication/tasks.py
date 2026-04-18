from celery import shared_task
from .emails import (
    send_verification_email as _send_verification_email,
    send_password_reset_email as _send_password_reset_email,
    )


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_verification_email(self, user_email, uid, token):
    try:
        _send_verification_email(user_email, uid, token)
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email(self, user_email, uid, token):
    try:
        _send_password_reset_email(user_email, uid, token)
    except Exception as exc:
        raise self.retry(exc=exc)
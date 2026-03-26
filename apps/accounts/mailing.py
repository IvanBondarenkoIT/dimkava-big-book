"""Send transactional email for candidate verification."""
from urllib.parse import quote

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

from .email_verification import sign_user_id


def send_candidate_verification_email(request, user) -> None:
    token = sign_user_id(user.pk)
    link = request.build_absolute_uri(
        reverse('accounts:confirm_email') + '?token=' + quote(token, safe='')
    )
    subject = 'Confirm your email — Dim Kava'
    body = (
        f'Hi,\n\n'
        f'Please confirm your email to access learning content:\n\n'
        f'{link}\n\n'
        f'If you did not register, you can ignore this message.\n'
    )
    send_mail(
        subject,
        body,
        getattr(settings, 'DEFAULT_FROM_EMAIL', None) or 'noreply@localhost',
        [user.email],
        fail_silently=False,
    )

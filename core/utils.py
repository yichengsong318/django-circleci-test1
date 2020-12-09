import datetime
import secrets
from django.utils import timezone
from django.template.loader import get_template
from django.core.mail import EmailMessage

from core.models import PasswordResetKey
from saas_template.settings import (
    DEFAULT_RECOVERY_KEY_VALID_DAYS,
    EMAIL_ADDRESS_RECOVER_PASSWORD
)


def send_password_reset_email(user, store=None):
    """

    :param user:
    :param store:
    :return:
    """
    expires = timezone.now() + datetime.timedelta(
        days=DEFAULT_RECOVERY_KEY_VALID_DAYS)

    key = PasswordResetKey.objects.create(
        store=store,
        user=user,
        key=secrets.token_hex(32),
        expires=expires
    )

    # Use different templates for stores and normal users
    if store:
        template = "stores/email/password_reset_email.html"
    else:
        template = "core/email/password_reset_email.html"

    params = {
        "user": user,
        "key": key,
        "store": store
    }

    email_subject = "Reset your password."
    email_from = EMAIL_ADDRESS_RECOVER_PASSWORD
    email_body = get_template(template).render(params)

    message = EmailMessage(
        email_subject, email_body, email_from, [user.email])
    message.send()

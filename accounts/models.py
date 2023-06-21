from django.conf import settings
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail 
from django.contrib.auth.models import User
from django.db import models
from urllib.parse import urlencode, ParseResult


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    params = {'token':reset_password_token.key}
    path = reverse('password_reset:reset-password-request')
    query = urlencode(params)
    url = ParseResult(
        scheme=settings.DOMAIN_PROTOCOL,
        netloc=settings.DOMAIN_HOST,
        path=path,
        query=query,
        params='',
        fragment=''
    )
    email_plaintext_message = url.geturl()

    send_mail(
        # title:
        "Password Reset for {title}".format(title=settings.DOMAIN_HOST),
        # message:
        email_plaintext_message,
        # from:
        settings.DEFAULT_FROM_EMAIL,
        # to:
        [reset_password_token.user.email]
    )

class UserProfile(models.Model):
    MANUAL = 1
    SOCIAL = 2

    AUTHENTICATION_TYPE = (
        (MANUAL, 'Manual'),
        (SOCIAL, 'Social')
    )

    TWITER = 1
    GMAIL = 2
    FACEBOOK = 3

    AUTHENTICATION_LABEL = (
        (MANUAL, 'Manual'),
        (SOCIAL, 'Social')
    )

    user = models.OneToOneField(
        User, related_name='profile', on_delete=models.CASCADE)
    authentication_type = models.SmallIntegerField(choices=AUTHENTICATION_TYPE, default=MANUAL)
    authentication_label = models.SmallIntegerField(choices=AUTHENTICATION_LABEL, default=GMAIL)
    user_role = models.CharField(default='common', max_length=10, blank=True)
    country = models.CharField(max_length=30, blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    ip_address= models.CharField(max_length=30, blank=True)
    class Meta:
        db_table = 'user_profile'


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.IntegerField(default=0)
'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

from datetime import datetime

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string

from sxconsole.core import token_expiration


TOKEN_LENGTH = 16


class TokenManager(models.Manager):

    def get_queryset(self):
        return super(TokenManager, self).get_queryset().filter(
            expiration_date__gte=datetime.now())

    def expired(self):
        return super(TokenManager, self).get_queryset().filter(
            expiration_date__lt=datetime.now())


class TokenModel(models.Model):
    """Base for models with tokens."""
    token = models.CharField(max_length=TOKEN_LENGTH, unique=True)
    expiration_date = models.DateTimeField(default=token_expiration,
                                           editable=False)

    objects = TokenManager()

    class Meta:
        abstract = True


@receiver(pre_save)
def set_token(instance, **kwargs):
    """Set a random, unique token."""
    if isinstance(instance, TokenModel) and not instance.token:
        searching = True
        while searching:
            token = get_random_string(TOKEN_LENGTH)
            searching = type(instance).objects.filter(token=token).exists()
        instance.token = token

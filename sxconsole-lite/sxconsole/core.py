'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

import re
from datetime import datetime, timedelta
from random import randint

from django.conf import settings
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from sizefield.utils import filesizeformat
from sxclient import UserData
from sxclient.defaults import FILTER_NAME_TO_UUID

from sxconsole.api import api
from . import logger


version = '0.9.0'
"""SX Console version"""


_sep = '.'
"""Namespace separator for volume names.

For example, a volume 'foo' in a virtual cluster 'bar' will be named 'foo:bar'.
"""

_key_len = 20
"""Length of a user key."""


_admin_user_name = 'admin'
"""Username of an admin user."""

_reserved_user_names = {_admin_user_name}

_min_volume_size = 1024 ** 2

_min_replica_count = max(settings.APP_CONF.get('min_replicas'), 1)


def create_key(email, password):
    """Convert given data to a sx-usable auth key."""
    uuid = api.get_cluster_uuid()
    key = UserData.from_userpass_pair(email, password, uuid).key
    return key[20:40].encode('hex')  # Return private part only


identifier_re = re.compile(r'^[a-zA-Z0-9-_]{2,}$')
"""Regex for cluster and volume names."""


identifier_validator = validators.RegexValidator(
    identifier_re,
    message=_(
        "Name should consist of at least two characters and include "
        "only alphanumeric characters, hyphen and underscore."))

max_objects_validator = validators.MaxValueValidator(2 ** 16)


password_validator = validators.MinLengthValidator(8)


def size_validator(value):
    if value < _min_volume_size and value != 0:
        raise ValidationError(_("Size must be either 0 or at least 1MB."))


def replicas_validator(value):
    nodes_count = len(api.listNodes()['nodeList'])
    if value < _min_replica_count or value > nodes_count:
        raise ValidationError(
            _("Replicas must be between {min} and {max}.")
            .format(min=_min_replica_count, max=nodes_count))


def revisions_validator(value):
    """
    >>> revisions_validator(65)
    Traceback (most recent call last):
        ...
    ValidationError: ...
    >>> revisions_validator(0)
    Traceback (most recent call last):
        ...
    ValidationError: ...
    >>> revisions_validator(8)
    """
    min, max = 1, 64
    if value < min or value > max:
        raise ValidationError(
            _("Revisions must be between {min} and {max}.")
            .format(min=min, max=max))


def token_expiration():
    """Generate an expiration date for a token."""
    return datetime.now() + timedelta(days=2)


def random_bytes(length):
    """Returns a random binary string.

    For convenience, it's already hex-encoded to work with sxclient.
    """
    bytes = (chr(randint(0, 255)) for i in range(length))
    return ''.join(bytes).encode('hex')


def generate_user_key():
    """Generate a random user key."""
    return random_bytes(20)


def generate_encryption_meta():
    """Returns volumeMeta dict for encrypted volumes."""
    meta = {
        'filterActive': 'aes256'  # SXClient replaces this with the uuid
    }
    cfg_key = '{}-cfg'.format(FILTER_NAME_TO_UUID['aes256'])
    meta[cfg_key] = random_bytes(17)
    return meta


_invalid_volume_size_re = re.compile(r'.* between (\d+) and (\d+)')


def get_exception_msg(e):
    """Executed when SXClientException occurs in views.

    Exception message will be checked against known errors, and a prepared
    message will be returned to the user.
    If it isn't a known error, log the message since it might've not been
    handled properly.

    Returns a (field_name, error) tuple.
    """
    if 'Max retries exceeded' in e.message or \
            'Failed to query cluster' in e.message:
        return _("Connection to the cluster failed.")
    elif 'Invalid volume size' in e.message:
        match = _invalid_volume_size_re.match(e.message)
        if match:
            min_, max_ = match.groups()
            return _("Volume size should be between {min} and {max}.") \
                .format(min=filesizeformat(min_), max=filesizeformat(max_))
    logger.warning(
        "Unknown exception ocurred. "
        "The user will be shown a generic error message.\n"
        "Exception: " + e.message)
    return _("An error occurred while processing your request. "
             "Please try again later.")

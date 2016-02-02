'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

from datetime import datetime, timedelta

import pytest
from django.core.exceptions import ValidationError
from sxclient import UserData
from sxclient.defaults import FILTER_NAME_TO_UUID

from sxconsole import core


def test_create_key(api):
    username = 'foo'
    password = 'bar'
    key = UserData.from_userpass_pair(username, password,
                                      api.get_cluster_uuid()).key
    key = key[20:40].encode('hex')
    assert core.create_key(username, password) == key


def test_identifier_re():
    assert core.identifier_re.match('foo.bar') is None, \
        "Must not match the namespace separator."


class TestSizeValidator:
    """Should be valid for either 0 or at least 1mb"""

    @pytest.mark.parametrize('value', [0, 1024 ** 2, 1024 ** 3])
    def test_valid(self, value):
        core.size_validator(value)

    @pytest.mark.parametrize('value', [-1, 1024, 1024 ** 2 - 1])
    def test_invalid(self, value):
        with pytest.raises(ValidationError):
            core.size_validator(value)


def test_replicas_validator(api):
    """Replicas can't be greater than the number of nodes."""
    nodes_count = len(api.listNodes()['nodeList'])

    core.replicas_validator(1)
    core.replicas_validator(nodes_count)

    with pytest.raises(ValidationError):
        core.replicas_validator(0)
    with pytest.raises(ValidationError):
        core.replicas_validator(nodes_count + 1)


def test_revisions_validator():
    """Revisions must be between 1 and 64."""
    core.revisions_validator(1)
    core.revisions_validator(64)

    with pytest.raises(ValidationError):
        core.revisions_validator(0)
    with pytest.raises(ValidationError):
        core.revisions_validator(65)


def test_token_expiration():
    """Tokens shouldn't be valid for long periods of time."""
    now = datetime.now()
    expiration = core.token_expiration()
    assert now < expiration
    assert expiration < now + timedelta(days=7)


def test_random_bytes():
    """Should return a random hex-encoded binary string of given length."""
    length = 5
    bytes = core.random_bytes(length)
    assert len(bytes.decode('hex')) == length
    assert bytes != core.random_bytes(length)


def test_generate_user_key():
    """Should return a random 20-byte hex-encoded string."""
    key = core.generate_user_key()
    assert key != core.generate_user_key()
    decoded_key = key.decode('hex')
    assert len(decoded_key) == 20


def test_generate_encryption_meta():
    """Should return volumeMeta for aes256 filter."""
    meta = core.generate_encryption_meta()
    assert meta['filterActive'] == 'aes256'  # SXClient converts this to UUID
    cfg_key = '{}-cfg'.format(FILTER_NAME_TO_UUID['aes256'])
    cfg_val = meta[cfg_key].decode('hex')
    assert len(cfg_val) == 17  # Must be 17 ran

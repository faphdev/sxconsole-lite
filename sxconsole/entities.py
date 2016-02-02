'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

from operator import itemgetter

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from sxclient.defaults import FILTER_NAME_TO_UUID

from sxconsole import core
from sxconsole.api import api


class Volume(object):

    def __init__(self, cluster, name, data):

        self.cluster = cluster
        self.name = name

        self.size = data['sizeBytes']
        self.used_size = data['usedSize']
        self.revisions = data['maxRevisions']
        self.replicas = data['replicaCount']

        self.encryption = data['volumeMeta'].get('filterActive') == \
            FILTER_NAME_TO_UUID['aes256']

    @property
    def empty(self):
        return not self.used_size

    @property
    def acl(self):
        """Filter volume acl to keep the cluster's users only."""
        acl = api.getVolumeACL(self.name)
        acl = {k.lower(): v for k, v in acl.items()}

        volume_acl = []
        for user in self.cluster.users:
            email = user.email.lower()
            perms = set(acl.get(email, []))
            volume_acl.append({
                'email': email,
                'is_reserved': user.is_reserved,
                'read': 'read' in perms,
                'write': 'write' in perms,
                'manager': 'manager' in perms,
            })

        return sorted(volume_acl, key=itemgetter('email'))

    def get_user_acl(self, email):
        for perm in self.acl:
            if email.lower() == perm['email'].lower():
                return perm
        else:
            raise ValueError("No such user ({user}) in volume {volume}."
                             .format(user=email, volume=self.name))


class User(object):

    is_reserved = False

    def __init__(self, cluster, email, data):
        self.cluster = cluster
        self.email = email

        if self.email in core._reserved_user_names:
            self.is_reserved = True

        try:
            validate_email(self.email)
            self.has_valid_email = True
        except ValidationError:
            self.has_valid_email = False

'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

from sxconsole.api import api
from sxconsole import core


def get_free_size(cluster):
    used_space = sum(v.size for v in cluster.volumes)
    return max(cluster.size - used_space, 0)


def create_volume(name, size, replicas, revisions, encryption=None):
    """
    For given volume parameters, creates a volume inside the vcluster.
    """
    owner = core._admin_user_name

    meta = {}
    if encryption:
        meta.update(core.generate_encryption_meta())

    api.createVolume(
        volume=name, volumeSize=size, owner=owner,
        replicaCount=replicas, maxRevisions=revisions,
        volumeMeta=meta)


def create_user(email, password=None):
    """Creates a user."""

    if password:
        key = core.create_key(email, password)
    else:
        key = core.generate_user_key()

    api.createUser(email, userType='normal', userKey=key)

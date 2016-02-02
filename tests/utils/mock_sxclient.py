'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

import uuid
from copy import deepcopy

from sxclient.exceptions import (
    SXClusterBadRequest, SXClusterClientError, SXClusterNonFatalError,
    SXClusterNotFound)


def mock_api(api):
    """
    Given a `sxconsole.api.Api` instance, patch its methods with mock
    functions.
    """
    CLUSTER_UUID = str(uuid.uuid4())
    NODES = {'nodeList': ['127.0.0.1', '127.0.0.2', '127.0.0.3', '127.0.0.4']}
    USERS = {}
    VOLUMES = {}
    ACL = {}

    # User ops

    api.listUsers = lambda: deepcopy(USERS)

    def createUser(username, quota=None, desc=None, **kwargs):
        if username in USERS:
            raise SXClusterNonFatalError('User already exists')
        user = {'userQuota': quota or 0}
        if desc is not None:
            user['userDesc'] = desc
        USERS[username] = user
    api.createUser = createUser

    def modifyUser(username, quota=None, **kwargs):
        try:
            user = USERS[username]
        except KeyError:
            raise SXClusterNotFound('No such user')
        if quota is not None:
            user['userQuota'] = quota
    api.modifyUser = modifyUser

    def removeUser(username, *args, **kwargs):
        try:
            USERS.pop(username)
        except KeyError:
            raise SXClusterNotFound('No such user')
    api.removeUser = removeUser

    # Volume ops

    def listVolumes(includeMeta=False):
        volumes = deepcopy(VOLUMES)
        if not includeMeta:
            for v in volumes.values():
                v.pop('volumeMeta')
        return {'volumeList': volumes}
    api.listVolumes = listVolumes

    def createVolume(volume, owner, volumeSize, maxRevisions, replicaCount,
                     volumeMeta=None, **kwargs):
        if volume in VOLUMES:
            raise SXClusterNonFatalError('Volume already exists')
        elif owner != 'admin' and owner not in USERS:
            raise SXClusterBadRequest(
                'Invalid volume owner: user does not exist')
        else:
            VOLUMES[volume] = {
                'owner': owner,
                'sizeBytes': volumeSize,
                'usedSize': 0,
                'maxRevisions': maxRevisions,
                'replicaCount': replicaCount,
                'volumeMeta': deepcopy(volumeMeta or {}),
            }
            ACL[volume] = {'admin': ['read', 'write', 'manager', 'owner']}
    api.createVolume = createVolume

    def modifyVolume(volume, owner=None, size=None, maxRevisions=None):
        try:
            volume = VOLUMES[volume]
        except KeyError:
            raise SXClusterNotFound("Volume does not exist")
        if owner is not None:
            if owner not in USERS:
                raise SXClusterNotFound("User not found")
            volume['owner'] = owner
        if size is not None:
            volume['size'] = size
        if maxRevisions is not None:
            volume['maxRevisions'] = maxRevisions
    api.modifyVolume = modifyVolume

    def deleteVolume(name, force=False):
        try:
            volume = VOLUMES[name]
        except KeyError:
            raise SXClusterNotFound("No such volume")
        if force is False and volume['usedSize'] > 0:
            raise SXClusterClientError("Cannot delete non-empty volume")
        else:
            VOLUMES.pop(name)
            ACL.pop(name)
    api.deleteVolume = deleteVolume

    # ACL ops

    def getVolumeACL(volume):
        try:
            return deepcopy(ACL[volume])
        except KeyError:
            raise SXClusterNotFound("No such volume")
    api.getVolumeACL = getVolumeACL

    def updateVolumeACL(volume, actions):
        try:
            acl = ACL[volume]
        except KeyError:
            raise SXClusterNotFound("No such volume")

        valid_perms = {'read', 'write', 'manager'}
        valid_actions = {'grant', 'revoke'}
        valid_users = set(USERS.keys())

        error = SXClusterBadRequest("Invalid ACL params")

        def process_user(user, action, perm):
            """Updates the user's acl."""
            if user not in valid_users:
                raise SXClusterBadRequest("No such user: {}".format(user))
            user_acl = acl.setdefault(user, [])
            if action == 'grant' and perm not in user_acl:
                user_acl.append(perm)
            elif action == 'revoke' and perm in user_acl:
                user_acl.remove(perm)
            if not user_acl:
                acl.pop(user)

        for action, users in actions.items():
            # Convert key to acl entry, e.g. 'grant-read' -> {'read': True}
            try:
                action, perm = action.split('-')
            except ValueError:
                raise error
            if perm not in valid_perms:
                raise error
            if action not in valid_actions:
                raise error
            # Update users' acl according to given rule
            for user in users:
                process_user(user, action, perm)
    api.updateVolumeACL = updateVolumeACL

    # Misc ops

    api.has_encryption = True
    api.listNodes = lambda: deepcopy(NODES)
    api.get_cluster_uuid = lambda: CLUSTER_UUID

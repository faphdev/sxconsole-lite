'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''


class TestMockApi:
    def test_acl(self, api):
        volume, username = 'my_volume', 'user@example.com'
        api.createVolume(volume, owner='admin', volumeSize=1, maxRevisions=1,
                         replicaCount=1)
        api.createUser(username)

        acl = api.getVolumeACL(volume)
        assert acl.keys() == ['admin']

        api.updateVolumeACL(volume, {'grant-manager': [username]})
        acl = api.getVolumeACL(volume)
        assert set(acl.keys()) == {'admin', username}
        assert acl[username] == ['manager']

        api.updateVolumeACL(volume, {
            'grant-manager': [username],
            'grant-read': [username]})
        acl = api.getVolumeACL(volume)
        assert set(acl[username]) == {'read', 'manager'}

        api.updateVolumeACL(volume, {'revoke-write': [username],
                                     'revoke-manager': [username]})
        acl = api.getVolumeACL(volume)
        assert set(acl[username]) == {'read'}

        api.updateVolumeACL(volume, {'revoke-read': [username]})
        acl = api.getVolumeACL(volume)
        assert username not in acl

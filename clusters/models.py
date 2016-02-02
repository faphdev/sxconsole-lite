'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from sizefield.utils import filesizeformat

from sxconsole import core
from sxconsole.api import api
from sxconsole.entities import Volume, User


_default_settings = {
    'invitation_message': '\n'.join([
        "You have been invited to {app_name}.".format(
            app_name=settings.SKIN['app_name']),
        "",
        "Click the link below to join:",
        "{{link}}"])
}


class Cluster(object):
    """A fake cluster, within a physical cluster."""

    name = _("Your cluster")
    size = 0

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse('cluster_detail')

    @property
    def used_size(self):
        return sum(v.used_size for v in self.volumes)

    def get_used_size_display(self):
        usage = self.used_size
        size = self.size
        if size:
            percentage = int(round(100. * usage / size))
            return _("{usage} of {size} ({percentage}%)").format(
                usage=filesizeformat(usage), size=filesizeformat(size),
                percentage=percentage)
        else:
            return filesizeformat(usage)

    def get_allocated_size_display(self):
        allocated = sum(v.size for v in self.volumes)
        size = self.size
        if size:
            percentage = int(round(100. * allocated / size))
            return _("{usage} of {size} ({percentage}%)").format(
                usage=filesizeformat(allocated), size=filesizeformat(size),
                percentage=percentage)
        else:
            return filesizeformat(allocated)

    def build_name(self, volume_name):
        """Given a volume name, return a full volume name."""
        if self.is_root:
            return volume_name
        return core.build_name(self.name, volume_name)

    @property
    def volumes(self):
        """Get a list of volumes in this cluster."""

        all_volumes = api.listVolumes(includeMeta=True)['volumeList']
        volumes = [Volume(self, name, data)
                   for name, data in all_volumes.items()]
        return sorted(volumes, key=lambda v: v.name)

    def get_volume(self, name, refresh=False):
        """Return a volume based on the given name.

        If `refresh` is True, volumes cache will be reloaded first."""
        if refresh:
            try:
                del self.volumes
            except AttributeError:
                pass  # Cache was empty
        for volume in self.volumes:
            if volume.name == name:
                return volume
        raise ValueError('No such volume: {}'.format(name))

    def can_be_deleted(self):
        return not (self.volumes or self.users)

    @property
    def users(self):
        """Get a list of users in this cluster.

        Unlike volumes, user emails are not prefixed with cluster name.
        """
        all_users = api.listUsers()
        users = [User(self, email, data) for email, data in all_users.items()]
        return sorted(users, key=lambda u: (u.is_reserved, u.email))

    def get_user(self, email, refresh=False):
        """Return a user based on the given email.

        If `refresh` is True, users cache will be reloaded first."""
        if refresh:
            try:
                del self.users
            except AttributeError:
                pass  # Cache was empty
        for user in self.users:
            if user.email == email:
                return user
        raise ValueError('No such user: {}'.format(email))


cluster = Cluster()

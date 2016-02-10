'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

from django.utils.translation import ugettext_lazy as _

from utils import clusters


def validate_volume_size(cluster, size, current_size):
    """
    Called when creating/updating a volume, to check its new size against
    cluster limits.
    """
    if (
            cluster.size == 0 or
            (current_size != 0 and size < current_size)
    ):
        return True, None
    max_size = clusters.get_free_size(cluster) - current_size
    if size > max_size:
        return False, _(
            "You are running out of space on this cluster. "
            "Enter a smaller size and try again.")
    return True, None


def validate_name(cluster, name):
    name = name.lower()
    for volume in cluster.volumes:
        if name == volume.name.lower():
            return False, _("This volume already exists.")
    return True, None

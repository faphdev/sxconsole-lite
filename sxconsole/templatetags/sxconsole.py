'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

from __future__ import absolute_import

from django.template import Library
from django.utils.html import format_html

from clusters.models import Cluster
from sxconsole.entities import Volume


register = Library()


@register.filter(name='icon')
def icon(value, args=''):
    classes = ['fa'] + args.split()
    if isinstance(value, Cluster):
        classes.append('fa-server')
    elif isinstance(value, Volume):
        classes.append('fa-archive')
    else:
        raise TypeError(
            "Unknown type ({}) passed to `icon` filter."
            .format(type(value)))
    return format_html('<span class="{}"></span>', ' '.join(classes))

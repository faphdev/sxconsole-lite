'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

import subprocess

from django.conf import settings

from clusters.models import cluster


def sx_console(request):
    context = {
        'BASE_TEMPLATE': 'base.html' if request.user.is_authenticated()
        else 'public_base.html',
        'VERSION': subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD']).strip(),
        'SKIN': settings.SKIN,
        'DEMO': settings.DEMO,
        'ENTERPRISE_URL': 'http://skylable.com/products/enterprise/',
    }
    if request.user.is_authenticated():
        clusters = [cluster]
        context['side_panel'] = {
            'clusters': clusters,
            'clusters_count': len(clusters),
        }
    return context

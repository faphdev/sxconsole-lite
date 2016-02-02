'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

from socket import error as SocketError

from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail as dj_send_mail

from sxconsole import logger


def send_mail(request, subject, to, template=None, context=None, content=None):
    """Useful wrapper around django's send_mail."""

    if isinstance(to, basestring):
        to = [to]  # send_mail expects a list of recipients

    if not content:
        if 'link' in context:
            context['link'] = request.build_absolute_uri(context['link'])
        content = render_to_string(template, context)
    content = content.strip()

    from_ = settings.DEFAULT_FROM_EMAIL

    try:
        dj_send_mail(subject, content, from_, to)
        return True
    except SocketError as e:
        logger.error("Failed to send e-mail: {}".format(e))
        return False

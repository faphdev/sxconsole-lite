'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

import re

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from sxconsole.api import api
from sxconsole.core import create_key
from utils.models import TokenModel
from utils.mail import send_mail

app_name = settings.SKIN['app_name']


class UserPasswordReset(TokenModel):
    """Password reset for virtual cluster users."""
    email = models.EmailField()

    @property
    def reset_link(self):
        return reverse('cluster_user_password_reset', args=[self.token])

    @property
    def invitation_link(self):
        return reverse('cluster_user_invitation', args=[self.token])

    def consume(self, password):
        """Set the password and delete all tokens."""
        api.modifyUser(self.email, create_key(self.email, password))
        UserPasswordReset.objects.filter(email=self.email).delete()

    def send_reset(self, request):
        """Send an email with the password reset link."""
        subject = _("{app_name} password reset").format(app_name=app_name)
        tpl = 'mail/password_reset.html'
        ctx = {
            'app_name': app_name,
            'link': self.reset_link,
        }
        return send_mail(request, subject, self.email, tpl, ctx)

    def send_invitation(self, request, tpl):
        """Send an email with the invitation."""
        subject = _("Welcome to {app_name}!").format(app_name=app_name)

        link = request.build_absolute_uri(self.invitation_link)
        content = re.sub('{{ *link *}}', link, tpl)
        return send_mail(request, subject, self.email, content=content)

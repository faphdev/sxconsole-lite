'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from dj.choices import Choices
from dj.choices.fields import ChoiceField

from utils.mail import send_mail
from utils.models import TokenModel

console_app_name = settings.SKIN['console_app_name']


class AdminLevels(Choices):
    """Choices for Admin level."""
    _ = Choices.Choice

    ADMIN = _("Admin")
    ROOT_ADMIN = _("Root Admin")


class Admin(AbstractBaseUser):
    """An user of the console. Only admins have access to the console."""
    LEVELS = AdminLevels
    USERNAME_FIELD = 'email'

    email = models.EmailField(verbose_name=_("Email"), unique=True)
    level = ChoiceField(verbose_name=_("Level"), choices=LEVELS,
                        default=LEVELS.ADMIN)

    objects = BaseUserManager()

    class Meta:
        ordering = ('-level', 'email')

    @property
    def is_root_admin(self):
        return self.level == self.LEVELS.ROOT_ADMIN


class PasswordReset(TokenModel):
    """Token for resetting passwords."""
    admin = models.ForeignKey(Admin)

    def consume(self, password):
        """Set the password and remove the token."""
        if not settings.DEMO:
            self.admin.set_password(password)
            self.admin.save()
        PasswordReset.objects.filter(admin=self.admin).delete()

    def send_reset(self, request):
        """Send an email with the password reset link."""
        subject = _("{app_name} password reset") \
            .format(app_name=console_app_name)
        tpl = 'mail/password_reset.html'
        url_name = 'password_reset'

        ctx = {
            'app_name': console_app_name,
            'link': reverse(url_name, args=[self.token])
        }
        return send_mail(request, subject, self.admin.email, tpl, ctx)

    def send_invitation(self, request):
        """Send an email with the invitation."""
        subject = _("Welcome to {app_name}!") \
            .format(app_name=console_app_name)
        tpl = 'mail/invite.html'
        url_name = 'invitation'

        ctx = {
            'app_name': console_app_name,
            'link': reverse(url_name, args=[self.token])
        }
        return send_mail(request, subject, self.admin.email, tpl, ctx)

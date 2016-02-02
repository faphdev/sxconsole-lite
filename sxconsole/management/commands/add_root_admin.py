'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from accounts.models import Admin


class Command(BaseCommand):
    help = 'Creates a Root Admin user'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str)
        parser.add_argument('password', type=str)

    def handle(self, *args, **kwargs):
        email = kwargs['email']
        password = kwargs['password']
        admin = Admin(level=Admin.LEVELS.ROOT_ADMIN, email=email)
        admin.set_password(password)

        try:
            admin.full_clean()
        except ValidationError as e:
            raise CommandError(e)

        admin.save()
        self.stdout.write('Root admin {} created.'.format(email))

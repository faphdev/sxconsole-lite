'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

import factory

from accounts.models import Admin


class AdminFactory(factory.django.DjangoModelFactory):
    email = factory.Sequence('admin{}@example.com'.format)

    class Meta:
        model = Admin

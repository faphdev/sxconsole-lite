# -*- coding: utf-8 -*-
'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

from __future__ import unicode_literals

from django.db import migrations, models
import accounts.models
import dj.choices.fields
from django.conf import settings
import sxconsole.core


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('email', models.EmailField(unique=True, max_length=254, verbose_name='Email')),
                ('level', dj.choices.fields.ChoiceField(default=1, verbose_name='Level', choices=accounts.models.AdminLevels)),
            ],
            options={
                'ordering': ('-level', 'email'),
            },
        ),
        migrations.CreateModel(
            name='PasswordReset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('token', models.CharField(unique=True, max_length=16)),
                ('expiration_date', models.DateTimeField(default=sxconsole.core.token_expiration, editable=False)),
                ('admin', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

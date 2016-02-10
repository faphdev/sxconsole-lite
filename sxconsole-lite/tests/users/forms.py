'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

from __future__ import absolute_import

from users.forms import UserForm


class TestUserForm:
    def test_option_required(self):
        data = {
            'email': 'ffigiel@skylable.com',
        }
        assert 'option' in UserForm(data).errors

    def test_option_invalid(self):
        data = {
            'email': 'ffigiel@skylable.com',
            'option': 'yak-shaving',
        }
        assert 'option' in UserForm(data).errors

    def test_option_invite(self):
        data = {
            'email': 'ffigiel@skylable.com',
            'option': 'invite',
            'message': 'Some link: {{ link }}',
        }
        assert not UserForm(data).errors

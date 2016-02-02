'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

from sxconsole.api import api


def validate_email(email):
    email = email.lower()
    for user_email in api.listUsers().keys():
        if email == user_email.lower():
            return False, "Username not available"
    return True, None

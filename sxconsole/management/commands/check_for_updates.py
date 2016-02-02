'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

import requests
from django.core.management.base import BaseCommand

from sxconsole import logger
from sxconsole.core import version


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        version_msg = "Current SX Console version: {}".format(version)
        try:
            resp = requests.get(
                'http://cdn.skylable.com/check/sxconsole-lite-version')
        except Exception as e:
            msg = version_msg + ".\nFailed to check for updates. Error: {}."
            logger.error(msg.format(e))
            return
        if resp.ok:
            msg = version_msg + ", latest version: {}"
            logger.info(msg.format(resp.text))
        else:
            msg = version_msg + ". Failed to check for updates ({}). "
            logger.warn(msg.format(resp.status_code))

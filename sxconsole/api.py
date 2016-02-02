'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''
from functools import wraps
from time import time

from django.conf import settings
from django.utils.functional import cached_property
from sxclient import Cluster, UserData, SXController, SXFileCat, SXFileUploader

from sxconsole import logger


logger = logger.getChild('api')


def logged_calls(func):
    """Decorator for logging api calls."""
    @wraps(func)
    def wrapped(*args, **kwargs):
        operation = func.im_class.__name__
        logger.debug("Calling '{}'".format(operation))

        start = time()
        result = func(*args, **kwargs)
        total = time() - start

        if total > 1:
            logger.warn("Operation '{}' finished in {}s"
                        .format(operation, total))
        return result
    return wrapped


def get_api():

    class Api(object):
        """Provides a simplified sxclient experience."""

        def __init__(self, conf):
            self._cluster = self._get_cluster(conf)
            self._user_data = self._get_user_data(conf)
            self._sx = SXController(self._cluster, self._user_data)

            for name in self._sx.available_operations:
                # Wrap api functions
                func = getattr(self._sx, name).json_call
                # Log performed actions
                func = logged_calls(func)
                setattr(self, name, func)

            self.downloader = SXFileCat(self._sx)
            self.uploader = SXFileUploader(self._sx)

        def get_cluster_uuid(self):
            return self._sx.get_cluster_uuid()

        def _get_user_data(self, conf):
            if 'admin_key' in conf:
                return UserData.from_key(conf['admin_key'])
            elif 'admin_key_path' in conf:
                return UserData.from_key_path(conf['admin_key_path'])
            else:
                raise ValueError(
                    "You must provide either 'admin_key' or 'admin_key_path' "
                    "in the sx config.")

        def _get_cluster(self, conf):
            ip_addresses = conf.get('ip_addresses')
            if isinstance(ip_addresses, basestring):
                ip_addresses = [ip_addresses]
            kwargs = {
                'name': conf.get('cluster'),
                'ip_addresses': ip_addresses,
                'is_secure': conf.get('is_secure', True),
                'port': conf.get('port'),
                'verify_ssl_cert':
                conf.get('certificate') or conf.get('verify_ca')
            }
            return Cluster(**kwargs)

        @cached_property
        def has_encryption(self):
            node = self.getNodeStatus(self.listNodes()['nodeList'][0])
            return node['libsxclientVersion'].startswith('2.0')

    return Api(settings.SX_CONF)

api = get_api()

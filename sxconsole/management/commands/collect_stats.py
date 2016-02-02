'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

import pickle
import socket
import struct
import time
from contextlib import closing

from django.core.management.base import BaseCommand
from sxconsole.api import api


class Command(BaseCommand):
    help = \
        'Obtains nodes and cluster statistics and stores them in the database'

    can_import_settings = True

    def handle(self, *args, **kwargs):
        from django.conf import settings
        with closing(socket.socket()) as sock:
            sock.connect((
                settings.CARBON_CONF['carbon_host'],
                settings.CARBON_CONF['port']))
            self.timestamp = int(time.time())
            self.sock = sock
            self.collect_cluster_stats()

    def collect_cluster_stats(self):
        volumes = api.listVolumes()['volumeList']
        used_size = sum(v['usedSize'] for v in volumes.itervalues())

        path = 'space_usage'

        data = [(path, (self.timestamp, used_size))]
        self.send_data(data)

    def send_data(self, tuples):
        payload = pickle.dumps(tuples, protocol=pickle.HIGHEST_PROTOCOL)
        header = struct.pack('!L', len(payload))
        self.sock.sendall(header)
        self.sock.sendall(payload)

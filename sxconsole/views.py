'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

import os
from operator import itemgetter
from datetime import timedelta
from itertools import chain
from time import time

import whisper
from dateutil.parser import parse as parse_date
from django.conf import settings
from django.http import JsonResponse
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from sxclient.exceptions import SXClientException

from sxconsole.api import api


class SuperAdminHomeView(generic.TemplateView):
    template_name = 'superadmin_home.html'
    title = _("Dashboard")
    url_name = 'home'

    @cached_property
    def zones(self):
        return api.getClusterStatus()['clusterStatus']['distributionModels']

    @cached_property
    def nodes(self):
        nodes = []
        for zone in self.zones:
            for node in zone:
                try:
                    nodes.append(api.getNodeStatus(node['nodeAddress']))
                except SXClientException:
                    return []
        return nodes

    def get_cluster_context(self):
        """Show info about the physical cluster."""

        nodes_down = not self.nodes

        def node_physical_size(node):
            return node['storageUsed'] + \
                node['fsAvailBlocks'] * node['fsBlockSize']

        cluster = {
            'address': 'sx://{}'.format(api._cluster.name or
                                        api._cluster.host),
            'port': api._cluster.port or (
                443 if api._cluster.is_secure else 80),
            'virtual_size': sum(n['nodeCapacity'] for n in chain(*self.zones)),
            'physical_size': sum(map(node_physical_size, self.nodes))
        }

        volumes = api.listVolumes()['volumeList'].values()
        vcluster_info = {
            'allocated_size': sum(v['sizeBytes'] for v in volumes),
            'count': 1
        }

        disk_usage = {
            'pre_replica': sum(v['usedSize'] for v in volumes),
            'post_replica': sum(n['storageUsed'] for n in self.nodes),
        }
        return {
            'nodes_down': nodes_down,
            'cluster': cluster,
            'vcluster_info': vcluster_info,
            'disk_usage': disk_usage,
        }

    def get_nodes_context(self):
        nodes_count = 0
        zones_info = []
        for i, zone in enumerate(self.zones):
            zone_nodes = []
            zones_info.append(zone_nodes)
            for j, data in enumerate(zone):
                nodes_count += 1
                node = {
                    'uuid': data['nodeUUID'],
                    'public_ip': data['nodeAddress'],
                    'private_ip': data.get('nodeInternalAddress'),
                    'capacity': data['nodeCapacity'],
                }
                zone_nodes.append(node)
                try:
                    data = api.getNodeStatus(data['nodeAddress'])
                except SXClientException:
                    node['down'] = True
                    continue
                node.update({
                    'sx_version': data['libsxclientVersion'],
                    'hashfs_version': data['hashFSVersion'].split()[-1],
                    'storage_path': data['nodeDir'],

                    'cores': data['cores'],
                    'memory': data['memTotal'],

                    'system': data['osType'] + ' ' + data['osRelease'],
                    'local_time': parse_date(data['localTime']),

                    'used_space': data['storageUsed'],
                    'free_space': data['fsAvailBlocks'] * data['fsBlockSize'],
                })
        return {
            'nodes_count': nodes_count,
            'zones': zones_info,
        }

    def get_context_data(self, **kwargs):
        context = {}
        context.update(self.get_cluster_context())
        context.update(self.get_nodes_context())
        context.update(kwargs)
        return super(SuperAdminHomeView, self).get_context_data(**context)


class StatsView(generic.TemplateView):
    template_name = 'stats.html'
    title = _("Statistics")
    url_name = 'stats'


class StatsBase(generic.View):
    """Base for displaying stats."""
    CLUSTER_STATS = {'space_usage'}

    def fetch(self, stat):
        if stat in self.CLUSTER_STATS:
            return self._fetch_cluster_stat(stat)
        else:
            raise ValueError('No such stat: {}'.format(stat))

    def _fetch(self, *parts):
        return whisper.fetch(
            os.path.join(settings.CARBON_CONF['whisper_dir'], *parts) + '.wsp',
            fromTime=self.from_time,
            untilTime=self.until_time)

    def _get_timestamps(self, args):
        ts = ['x']
        ts.extend(i * 1000 for i in xrange(*args))
        return ts

    def _dedupe(self, datasets):
        """Remove redundant points."""
        count = len(datasets[0])
        target_count = 100
        if count < target_count:
            return  # Too little data to care about dupes

        timestamps = datasets.pop(0)
        for data in datasets:
            assert len(timestamps) == len(data)

        dupes = []
        for i in xrange(3, len(timestamps)):
            if all((data[i - 1] == data[i] or data[i - 1] is None)
                   for data in datasets):
                dupes.append(i - 1)

        datasets.insert(0, timestamps)
        dupes.reverse()
        for i in dupes:
            for data in datasets:
                data.pop(i)

    def _fetch_cluster_stat(self, stat):
        range_args, data = self._fetch(stat)

        timestamps = self._get_timestamps(range_args)
        data.insert(0, stat)

        columns = [timestamps, data]
        self._dedupe(columns)
        return columns

    def _fetch_nodes_stat(self, stat):
        columns = []
        for node in self.nodes:
            range_args, data = self._fetch(stat, node['uuid'])
            data.insert(0, node['ip'])
            columns.append(data)

        timestamps = self._get_timestamps(range_args)
        columns.insert(0, timestamps)
        self._dedupe(columns)
        return columns

    @cached_property
    def nodes(self):
        zones = api.getClusterStatus()['clusterStatus']['distributionModels']
        nodes = ({'ip': node['nodeAddress'], 'uuid': node['nodeUUID']}
                 for node in chain(*zones))
        return sorted(nodes, key=itemgetter('ip'))

    @cached_property
    def until_time(self):
        return None


class InitialStatsView(StatsBase):
    """Return initial data for all stats."""
    url_name = 'initial_stats'

    def get(self, request, *args, **kwargs):
        data = {s: self.fetch(s) for s in self.CLUSTER_STATS}
        return JsonResponse(data)

    @cached_property
    def from_time(self):
        return int(time() - timedelta(hours=3).total_seconds())


class GetStatsView(StatsBase):
    """Return stats for a given stat name and time range."""
    url_name = 'get_stats'

    def get(self, request, *args, **kwargs):
        try:
            data = self.fetch(request.GET.get('stat'))
        except (TypeError, ValueError, whisper.InvalidTimeInterval):
            data = []
        return JsonResponse({'stats': data})

    @cached_property
    def from_time(self):
        try:
            return int(self.request.GET.get('from'))
        except (TypeError, ValueError):
            pass

    @cached_property
    def until_time(self):
        try:
            return int(self.request.GET.get('till'))
        except (TypeError, ValueError):
            pass

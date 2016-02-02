'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

from django.views import generic

from utils.views import ClusterViewMixin


class DisplayClusterView(ClusterViewMixin, generic.TemplateView):
    """Display a Cluster page."""
    template_name = 'clusters/cluster.html'
    url_name = 'cluster_detail'

    @property
    def title(self):
        return self.object.name

    def get_context_data(self, **kwargs):
        return super(DisplayClusterView, self).get_context_data(
            cluster=self.object, **kwargs)

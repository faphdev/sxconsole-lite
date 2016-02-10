'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

import pytest

from sxconsole.templatetags import sxconsole
from clusters.models import cluster


class TestIcon:
    def test_invalid(self):
        with pytest.raises(TypeError):
            sxconsole.icon(object())

    def test_cluster(self):
        regular_icon = sxconsole.icon(cluster)
        assert 'fa-globe' not in regular_icon
        assert 'fa-server' in regular_icon

'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

import pytest

from accounts.models import AdminLevels
from tests.utils import mock_api
from . import factories


@pytest.fixture(autouse=True)
def api():
    """Mock api functions."""
    from sxconsole.api import api
    mock_api(api)
    return api


@pytest.fixture
def user(db):
    return factories.AdminFactory()


@pytest.fixture
def super_user(db):
    return factories.AdminFactory(level=AdminLevels.SUPER_ADMIN)

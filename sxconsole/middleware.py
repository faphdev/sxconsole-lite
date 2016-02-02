'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

from django.conf import settings
from django.middleware.locale import LocaleMiddleware as DjLocaleMiddleware
from django.shortcuts import render_to_response
from django.utils.translation import LANGUAGE_SESSION_KEY
from django.utils.translation.trans_real import get_languages
from sxclient.exceptions import SXClientException

from .api import api


class ClusterConnectionMiddleware(object):
    """Checks if cluster connection is working.

    If cluster connection fails, an error page is returned.
    """
    cluster_unavailable_tpl = 'cluster_unavailable.html'

    def process_exception(self, request, exception):
        if isinstance(exception, SXClientException):
            try:
                api.listNodes()
            except SXClientException:
                response = render_to_response(self.cluster_unavailable_tpl)
                return response


class ExtendSessionMiddleware(object):

    def process_request(self, request):
        if request.user.is_authenticated() and request.session.get('remember'):
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)


class LocaleMiddleware(DjLocaleMiddleware):

    def process_request(self, request):
        if settings.APP_CONF.get('force_default_lang'):
            lang_code = request.session.get(LANGUAGE_SESSION_KEY)
            supported_lang_codes = get_languages()
            if lang_code not in supported_lang_codes:
                request.session[LANGUAGE_SESSION_KEY] = settings.LANGUAGE_CODE
        return super(LocaleMiddleware, self).process_request(request)

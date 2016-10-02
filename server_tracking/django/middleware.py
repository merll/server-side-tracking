# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from .settings import SERVER_SIDE_TRACKING as SST_SETTINGS
from .utils import process_pageview, process_exception


log = logging.getLogger(__name__)


class PageViewMiddleware(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        self.exclude = SST_SETTINGS['pageview_exclude']
        self.track_not_available = SST_SETTINGS['pageview_na_exceptions']
        self.track_exceptions = SST_SETTINGS['pageview_server_exceptions']
        self.track_ajax_responses = SST_SETTINGS['pageview_ajax_responses']
        self.track_ajax_exceptions = SST_SETTINGS['pageview_ajax_exceptions']

    def __call__(self, request):
        response = self.get_response(request)
        return self.process_response(request, response)

    def process_response(self, request, response):
        if 200 <= response.status_code < 300:
            if self.track_ajax_responses or not request.is_ajax():
                path = request.path_info.lstrip('/')
                if not any(path.startswith(exclude) for exclude in self.exclude):
                    try:
                        process_pageview(request, response)
                    except Exception as e:
                        log.exception(e)
        elif response.status_code == 404:
            if self.track_not_available:
                if self.track_ajax_exceptions or not request.is_ajax():
                    try:
                        process_exception(request, response, description=response.reason_phrase, fatal=0)
                    except Exception as e:
                        log.exception(e)
        elif response.status_code >= 400:
            if self.track_exceptions:
                if self.track_ajax_exceptions or not request.is_ajax():
                    try:
                        process_exception(request, response, description=response.reason_phrase, fatal=1)
                    except Exception as e:
                        log.exception(e)
        return response

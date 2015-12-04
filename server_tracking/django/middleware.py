# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from .settings import SST_SETTINGS
from .utils import process_pageview


log = logging.getLogger(__name__)


class PageViewMiddleware(object):
    def process_response(self, request, response):
        if not request.is_ajax():
            path = request.path_info.lstrip('/')
            if not any(path.startswith(exclude) for exclude in SST_SETTINGS['pageview_exclude']):
                try:
                    process_pageview(request, response)
                except Exception as e:
                    log.exception(e)
        return response

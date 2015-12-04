# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from .settings import SST_SETTINGS
from .utils import process_pageview


log = logging.getLogger(__name__)


class PageViewMixin(object):
    def dispatch(self, request, *args, **kwargs):
        response = super(PageViewMixin, self).dispatch(request, *args, **kwargs)
        if not request.is_ajax():
            path = request.path_info.lstrip('/')
            if not any(path.startswith(exclude) for exclude in SST_SETTINGS['pageview_exclude']):
                try:
                    process_pageview(request, response)
                except Exception as e:
                    log.exception(e)
        return response

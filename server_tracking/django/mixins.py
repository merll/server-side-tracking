# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from .middleware import PageViewMiddleware


log = logging.getLogger(__name__)


class PageViewMixin(object):
    def __init__(self, *args, **kwargs):
        super(PageViewMixin, self).__init__(*args, **kwargs)
        self._process_response = PageViewMiddleware().process_response

    def dispatch(self, request, *args, **kwargs):
        response = super(PageViewMixin, self).dispatch(request, *args, **kwargs)
        self._process_response(request, response)
        return response

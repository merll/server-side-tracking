# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse

from .utils import get_default_parameters, default_client, log


def track_event(category, action, label=None, value=None, misc_parameters=()):
    def event_decorator(func):
        def event_wrapper(self, *args, **kwargs):
            response = func(self, *args, **kwargs)
            param_response = response if isinstance(response, HttpResponse) else None
            try:
                pageview_params, session_params = get_default_parameters(self.request, param_response)
                default_client.event(category, action, label=label, value=value, page_params=pageview_params,
                                     session_params=session_params, misc_params=misc_parameters)
            except Exception as e:
                log.exception(e)

            return response

        return event_wrapper
    return event_decorator

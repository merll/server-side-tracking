# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http.response import HttpResponse
from django.views.generic import View

from . import utils

SESSION_PARAMETERS = (
    ('r', 'screen_resolution'),
    ('v', 'viewport_size'),
    ('c', 'screen_colors'),
)


class AnalyticsSessionParameterView(View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        response = HttpResponse(status=204)
        if utils.has_own_cookie(request):
            return response
        params = {}
        for url_param, s_param in SESSION_PARAMETERS:
            value = request.GET.get(url_param)
            if value:
                params[s_param] = value
        if params:
            utils.process_ping(request, response, session_parameters=params)
        return response


class OwnCookieView(View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        response = HttpResponse(status=204)
        utils.set_own_cookie(response)
        return response

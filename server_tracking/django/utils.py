# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import logging
from uuid import uuid4

from django.core.exceptions import ImproperlyConfigured
from django.utils.six import text_type

from .settings import SERVER_SIDE_TRACKING as SST_SETTINGS, SERVER_SIDE_TRACKING_GA as GA_SETTINGS
from ..google.client import AnalyticsClient
from ..google.parameters import GeneralParameters, SessionParameters, PageViewParameters
from ..google.sender import get_send_function
from ..utils import class_from_name, anonymize_ip_address


log = logging.getLogger(__name__)


class ContextTitleExtractor(object):
    def get_title(self, response):
        """
        :param response:
        :type response: django.http.response.HttpResponse
        :return:
        """
        return response.context_data.get('title')


class ViewTitleExtractor(object):
    def get_title(self, response):
        """

        :param response:
        :type response: django.http.response.HttpResponse
        :return:
        """
        view = response.context_data.get('view')
        if view:
            return view.title
        return None


def get_title_extractors():
    try:
        return [
            class_from_name(extractor)() for extractor in SST_SETTINGS['django_title_extractors']
        ]
    except (TypeError, AttributeError) as e:
        raise ImproperlyConfigured("Error in setting 'SERVER_SIDE_TRACKING' key 'django_title_extractors': "
                                   "{0}.".format(e.args[0]))


def extract_parameters(request, anonymize_ip):
    """
    :type request: django.http.HttpRequest
    :type anonymize_ip: bool
    :return: dict
    """
    get_meta = request.META.get
    get_params = request.GET.get
    remote_ip = get_meta('HTTP_X_FORWARDED_FOR')
    if not remote_ip:
        remote_ip = get_meta('REMOTE_ADDR')
    if remote_ip and anonymize_ip:
        ip_override = anonymize_ip_address(remote_ip)
    else:
        ip_override = remote_ip
    accept_language = get_meta('HTTP_ACCEPT_LANGUAGE')
    if accept_language:
        first_language = accept_language.partition(';')[0].split(',')[0]
    else:
        first_language = None
    return {
        'ip_override': ip_override,
        'user_agent_override': get_meta('HTTP_USER_AGENT'),
        'document_referrer': get_meta('HTTP_REFERER'),
        'user_language': first_language or None,
        'campaign_name': get_params('utm_campaign'),
        'campaign_source': get_params('utm_source'),
        'campaign_medium': get_params('utm_medium'),
        'campaign_keyword': get_params('utm_term'),
        'campaign_content': get_params('utm_content'),
        'google_adwords_id': get_params('gclid'),
        'google_display_ads_id': get_params('dclid'),
    }


def set_client_id(request, response, client_id, consent_action):
    if consent_action == 'refuse':
        c_accept = 0
        c_max_age = None
    elif consent_action == 'accept':
        c_accept = 1
        c_max_age = SST_SETTINGS['cookie_max_age']
    else:
        c_accept = None
        c_consent_status = request.COOKIES.get(SST_SETTINGS['cookie_accepted'])
        if c_consent_status:
            c_max_age = SST_SETTINGS['cookie_max_age']
        else:
            c_max_age = None

    if c_accept is not None:
        response.set_cookie(SST_SETTINGS['cookie_accepted'], c_accept,
                            path=SST_SETTINGS['cookie_path'],
                            expires='Fri, 31 Dec 9999 23:59:59 GMT')
    if consent_action:
        response.delete_cookie(SST_SETTINGS['cookie_action'], SST_SETTINGS['cookie_path'])
    response.set_signed_cookie(SST_SETTINGS['cookie_name'], client_id,
                               path=SST_SETTINGS['cookie_path'],
                               salt=SST_SETTINGS['cookie_salt'],
                               max_age=c_max_age,
                               secure=SST_SETTINGS['cookie_secure'],
                               httponly=SST_SETTINGS['cookie_httponly'])
    return client_id


def get_client(default_parameters=None, **kwargs):
    """
    :param default_parameters: Default parameters.
    :type default_parameters: server_tracking.google.parameters.GeneralParameters | dict
    :param kwargs: Additional general parameters.
    :return: Configured client.
    :rtype: server_tracking.google.client.AnalyticsClient
    """
    if default_parameters:
        default_params = GeneralParameters(default_parameters)
        if not default_params.tracking_id:
            default_params.tracking_id = GA_SETTINGS['property']
        default_params.update(kwargs)
    else:
        default_params = GeneralParameters(tracking_id=GA_SETTINGS['property'], **kwargs)
    send_function = get_send_function(SST_SETTINGS['defer'],
                                      ssl=GA_SETTINGS['ssl'],
                                      debug=SST_SETTINGS['debug'],
                                      default_method=SST_SETTINGS['send_method'],
                                      post_fallback=SST_SETTINGS['post_fallback'],
                                      timeout=SST_SETTINGS['timeout'])
    return AnalyticsClient(send_function, default_params)


def get_title(response):
    for ex in title_extractors:
        try:
            title = ex.get_title(response)
        except AttributeError:
            continue
        else:
            if title is not None:
                return title
    return None


def get_default_parameters(request, response, pageview_parameters=None, session_parameters=None):
    cid = request.get_signed_cookie(SST_SETTINGS['cookie_name'], default=None,
                                    salt=SST_SETTINGS['cookie_salt'],
                                    max_age=SST_SETTINGS['cookie_max_age'])
    if cid is None:
        cid = text_type(uuid4())
        updated_cid = True
    else:
        updated_cid = False
    c_consent_action = request.COOKIES.get(SST_SETTINGS['cookie_action'])
    if response:
        title = get_title(response)
        if updated_cid or c_consent_action:
            cid = set_client_id(request, response, cid, c_consent_action)
    else:
        title = None
    host_name = request.get_host().partition(':')[0]
    pageview_params = PageViewParameters(host_name=host_name, path=request.path, title=title)
    pageview_params.update(pageview_parameters)
    session_params = SessionParameters(extract_parameters(request, SST_SETTINGS['anonymize_ip']))
    session_params.client_id = cid
    session_params.update(session_parameters)
    return pageview_params, session_params


def process_pageview(request, response, pageview_parameters=None, session_parameters=None):
    pageview_params, session_params = get_default_parameters(request, response,
                                                             pageview_parameters=pageview_parameters,
                                                             session_parameters=session_parameters)
    return default_client.pageview(pageview_params, session_params=session_params)


def process_ping(request, response, pageview_parameters=None, session_parameters=None):
    pageview_params, session_params = get_default_parameters(request, response,
                                                             pageview_parameters=pageview_parameters,
                                                             session_parameters=session_parameters)
    return default_client.event(GA_SETTINGS['ping_category'], GA_SETTINGS['ping_action'],
                                label=GA_SETTINGS['ping_label'], non_interaction_hit=1, page_params=pageview_params,
                                session_params=session_params)


default_client = get_client()
title_extractors = get_title_extractors()

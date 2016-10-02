# -*- coding: utf-8 -*-
from six import iteritems


SST_DEFAULT_SETTINGS = {
    'cookie_name': 'vn',
    'cookie_action': 'cookie_action',
    'cookie_status': 'cookie_status',
    'cookie_status_refused': 0,
    'cookie_status_accepted': 1,
    'cookie_max_age': 63072000,
    'cookie_path': '/',
    'cookie_salt': '',
    'cookie_httponly': True,
    'cookie_secure': True,
    'debug': False,
    'send_method': 'GET',
    'post_fallback': True,
    'timeout': 10,
    'defer': None,
    'anonymize_ip': True,
    'pageview_exclude': (),
    'pageview_na_exceptions': False,
    'pageview_server_exceptions': False,
    'pageview_ajax_responses': False,
    'pageview_ajax_exceptions': False,
}
GA_DEFAULT_SETTINGS = {
    'ssl': True,
    'ping_category': 'Non-interaction',
    'ping_action': 'Ping',
    'ping_label': None,
}


def update_default_settings(settings, settings_var, default):
    config = getattr(settings, settings_var)
    if config:
        for k, v in iteritems(default):
            config.setdefault(k, v)
    else:
        config = default.copy()
        setattr(settings, settings_var, config)
    return config

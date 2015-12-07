# -*- coding: utf-8 -*-
from six import iteritems


SST_DEFAULT_SETTINGS = {
    'cookie_name': 'vn',
    'cookie_action': 'cookie_action',
    'cookie_accepted': 'cookies_accepted',
    'cookie_max_age': 63072000,
    'cookie_path': '/',
    'cookie_salt': '',
    'debug': False,
    'send_method': 'GET',
    'post_fallback': True,
    'timeout': 10,
    'defer': None,
    'anonymize_ip': True,
    'pageview_exclude': (),
}
GA_DEFAULT_SETTINGS = {
    'ssl': True,
    'ping_category': 'Non-interaction',
    'ping_action': 'Ping',
    'ping_label': None,
}

SST_SETTINGS = SST_DEFAULT_SETTINGS.copy()
GA_SETTINGS = GA_DEFAULT_SETTINGS.copy()


def update_default_settings(settings, settings_var, default):
    config = getattr(settings, settings_var)
    if config:
        for k, v in iteritems(default):
            config.setdefault(k, v)
    else:
        setattr(config, settings_var, default.copy())

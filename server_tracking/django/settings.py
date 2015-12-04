# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


SST_DEFAULT_SETTINGS = {
    'cookie_name': 'vn',
    'cookie_action': 'cookie_action',
    'cookie_accepted': 'cookies_accepted',
    'cookie_max_age': 63072000,
    'cookie_path': getattr(settings, 'SESSION_COOKIE_PATH', '/'),
    'cookie_salt': getattr(settings, 'SECRET_KEY', '/'),
    'debug': getattr(settings, 'DEBUG', False),
    'send_method': 'GET',
    'defer': None,
    'anonymize_ip': True,
    'pageview_exclude': [
        'admin/'
    ],
    'django_title_extractors': [
        'server_tracking.django.utils.ContextTitleExtractor',
        'server_tracking.django.utils.ViewTitleExtractor',
    ],
}
GA_DEFAULT_SETTINGS = {
    'ssl': True,
    'ping_category': 'Non-interaction',
    'ping_action': 'Ping',
    'ping_label': None,
}

SST_SETTINGS = SST_DEFAULT_SETTINGS.copy()
if hasattr(settings, 'SERVER_SIDE_TRACKING'):
    SST_SETTINGS.update(settings.SERVER_SIDE_TRACKING)

GA_SETTINGS = GA_DEFAULT_SETTINGS.copy()
if hasattr(settings, 'SERVER_SIDE_TRACKING_GA'):
    GA_SETTINGS.update(settings.SERVER_SIDE_TRACKING_GA)

if 'property' not in GA_SETTINGS:
    raise ImproperlyConfigured("SERVER_SIDE_TRACKING_GA must be defined in Django settings with a key 'property'.")

# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .. import DEFER_METHOD_CELERY
from ..settings import SST_DEFAULT_SETTINGS, GA_DEFAULT_SETTINGS, update_default_settings

SST_DEFAULT_SETTINGS.update(
    cookie_path=getattr(settings, 'SESSION_COOKIE_PATH', '/'),
    cookie_salt=getattr(settings, 'SECRET_KEY', ''),
    debug=getattr(settings, 'DEBUG', False),
    pageview_exclude=(
        'admin/',
    ),
    django_title_extractors=(
        'server_tracking.django.utils.ContextTitleExtractor',
        'server_tracking.django.utils.ViewTitleExtractor',
    ),
)

SERVER_SIDE_TRACKING = update_default_settings(settings, 'SERVER_SIDE_TRACKING', SST_DEFAULT_SETTINGS)
SERVER_SIDE_TRACKING_GA = update_default_settings(settings, 'SERVER_SIDE_TRACKING_GA', GA_DEFAULT_SETTINGS)

if SERVER_SIDE_TRACKING['defer'] == DEFER_METHOD_CELERY:
    from ..google import tasks

if 'property' not in SERVER_SIDE_TRACKING_GA:
    raise ImproperlyConfigured("SERVER_SIDE_TRACKING_GA must be defined in Django settings with a key 'property'.")

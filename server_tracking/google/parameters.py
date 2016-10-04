# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random
import sys

from ..exceptions import InvalidParametersException
from ..parameters import UP, UrlGenerator, EnumeratedUrlGenerator, PrefixUrlGenerator


class CustomDimensionUrlGenerator(UrlGenerator):
    class Meta(object):
        abstract = True
        custom_prefix = 'cd'


class CustomMetricUrlGenerator(UrlGenerator):
    class Meta(object):
        abstract = True
        custom_prefix = 'cm'


class GeneralParameters(UrlGenerator):
    # General
    protocol_version = UP('v', True)
    tracking_id = UP('tid', True)
    data_source = UP('ds', False)
    anonymize_ip = UP('aip', False)

    def __init__(self, params=None, use_cache_buster=False, **kwargs):
        super(GeneralParameters, self).__init__(params=params, **kwargs)
        if self.protocol_version is None:
            self.protocol_version = 1
        self._use_cache_buster = use_cache_buster

    def url(self, hit_type, *args, **kwargs):
        url = super(GeneralParameters, self).url(*args, **kwargs)
        url['t'] = hit_type
        if self._use_cache_buster:
            url['z'] = random.randint(0, sys.maxsize)
        return url

    @property
    def use_cache_buster(self):
        return self._use_cache_buster

    @use_cache_buster.setter
    def use_cache_buster(self, value):
        self._use_cache_buster = value


class HitParameters(UrlGenerator):
    queue_time = UP('qt', False)
    non_interaction_hit = UP('ni', False)


class SessionParameters(UrlGenerator):
    # User
    client_id = UP('cid', True)
    user_id = UP('uid', False)

    # Session
    session_control = UP('sc', False)
    ip_override = UP('uip', False)
    user_agent_override = UP('ua', False)
    geographical_override = UP('geoid', False)

    # Traffic source
    document_referrer = UP('dr', False)
    campaign_name = UP('cn', False)
    campaign_source = UP('cs', False)
    campaign_medium = UP('cm', False)
    campaign_keyword = UP('ck', False)
    campaign_content = UP('cc', False)
    campaign_id = UP('ci', False)
    google_adwords_id = UP('gclid', False)
    google_display_ads_id = UP('dclid', False)

    # System Info
    screen_resolution = UP('sr', False)
    viewport_size = UP('vp', False)
    document_encoding = UP('de', False)
    screen_colors = UP('sd', False)
    user_language = UP('ul', False)
    java_enabled = UP('je', False)
    flash_version = UP('fl', False)

    # Content experiments
    experiment_id = UP('xid', False)
    experiment_variant = UP('xvar', False)


class PageViewParameters(UrlGenerator):
    location_url = UP('dl', False)
    host_name = UP('dh', False)
    path = UP('dp', False)
    title = UP('dt', False)
    screen_name = UP('cd', False)
    link_id = UP('linkid', False)

    def __init__(self, params=None, location_url=None, host_name=None, path=None, title=None, **kwargs):
        super(PageViewParameters, self).__init__(params=params, location_url=location_url, host_name=host_name,
                                                 path=path, title=title, **kwargs)

    def validate(self):
        super(PageViewParameters, self).validate()
        if not self.location_url and (not self.host_name or not self.path):
            raise InvalidParametersException("Either 'location_url' must be specified, or both 'host_name' and 'path'.")


class AppTrackingParameters(UrlGenerator):
    name = UP('an', True)
    app_id = UP('aid', False)
    version = UP('av', False)
    installer_id = UP('aiid', False)


class EventParameters(UrlGenerator):
    category = UP('ec', True)
    action = UP('ea', True)
    label = UP('el', False)
    value = UP('ev', False)

    def __init__(self, category, action=None, label=None, value=None):
        super(EventParameters, self).__init__(category=category, action=action, label=label, value=value)


class AbstractEComUrlGenerator(UrlGenerator):
    transaction_id = UP('ti', True)
    currency_code = UP('cu', False)

    class Meta(object):
        abstract = True


class EComTransactionParameters(AbstractEComUrlGenerator):
    affiliation = UP('ta', False)
    revenue = UP('tr', False)
    shipping = UP('ts', False)
    tax = UP('tt', False)


class EComItemParameters(AbstractEComUrlGenerator):
    name = UP('in', True)
    price = UP('ip', False)
    quantity = UP('iq', False)
    code = UP('ic', False)
    category = UP('iv', False)

    @classmethod
    def from_item(cls, item, transaction_id, transaction_currency=None):
        return cls(transaction_id=transaction_id, name=item.name, price=item.price, quantity=item.quantity,
                   code=item.code, category=item.category, currency_code=item.currency_code or transaction_currency)


class EComItem(object):
    def __init__(self, name, price=None, quantity=None, code=None, category=None, currency_code=None):
        self.name = name
        self.price = price
        self.quantity = quantity
        self.code = code
        self.category = category
        self.currency_code = currency_code


class EnhancedEComProductParameters(EnumeratedUrlGenerator):
    sku = UP('id', False)
    name = UP('nm', False)
    brand = UP('br', False)
    category = UP('ca', False)
    variant = UP('va', False)
    price = UP('pr', False)
    quantity = UP('qt', False)
    coupon_code = UP('cc', False)
    position = UP('ps', False)

    class Meta(object):
        item_prefix = 'pr'


class EnhancedEComGeneralParameters(UrlGenerator):
    product_action = UP('pa', False)
    transaction_id = UP('ti', False)
    affiliation = UP('ta', False)
    revenue = UP('tr', False)
    tax = UP('tt', False)
    shipping = UP('ts', False)
    coupon_code = UP('tcc', False)
    product_action_list = UP('pal', False)
    checkout_step = UP('cos', False)
    checkout_step_option = UP('col', False)
    promotion_action = UP('promoa', False)


class EnhancedEComPIListParameters(PrefixUrlGenerator):
    name = UP('nm', False)

    class Meta(object):
        abstract = True
        preset_prefix = 'il'


class EnhancedEComPIProductParameters(EnumeratedUrlGenerator):
    sku = UP('id', False)
    name = UP('nm', False)
    brand = UP('br', False)
    category = UP('ca', False)
    variant = UP('va', False)
    position = UP('ps', False)
    price = UP('pr', False)

    class Meta(object):
        abstract = True
        preset_prefix = 'il'
        item_prefix = 'pi'


class EnhancedEComPICustomDimensionProductParameters(EnumeratedUrlGenerator):
    class Meta(object):
        abstract = True
        preset_prefix = 'il'
        item_prefix = 'pi'
        custom_prefix = 'cd'


class EnhancedEComPICustomMetricProductParameters(EnumeratedUrlGenerator):
    class Meta(object):
        abstract = True
        preset_prefix = 'il'
        item_prefix = 'pi'
        custom_prefix = 'cm'


class EnhancedEComPromotionParameters(PrefixUrlGenerator):
    promo_id = UP('id', False)
    name = UP('nm', False)
    creative = UP('cr', False)
    position = UP('ps', False)

    class Meta(object):
        abstract = True
        preset_prefix = 'promo'


class SocialInteractionParameters(UrlGenerator):
    network = UP('sn', True)
    action = UP('sa', True)
    target = UP('st', True)


class TimingParameters(UrlGenerator):
    user_timing_category = UP('utc', True)
    user_timing_variable = UP('utv', True)
    user_timing_value = UP('utt', True)
    user_timing_label = UP('utl', False)
    page_load_time = UP('plt', False)
    dns_time = UP('dns', False)
    page_download_time = UP('pdt', False)
    redirect_response_time = UP('rrt', False)
    tcp_connect_time = UP('tcp', False)
    server_response_time = UP('srt', False)
    dom_interactive_time = UP('dit', False)
    content_load_time = UP('clt', False)


class ExceptionParameters(UrlGenerator):
    description = UP('exd', False)
    fatal = UP('exf', False)

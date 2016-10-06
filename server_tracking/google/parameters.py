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
    data_source = UP('ds')
    anonymize_ip = UP('aip')

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
    queue_time = UP('qt')
    non_interaction_hit = UP('ni')


class SessionParameters(UrlGenerator):
    # User
    client_id = UP('cid', True)
    user_id = UP('uid')

    # Session
    session_control = UP('sc')
    ip_override = UP('uip')
    user_agent_override = UP('ua')
    geographical_override = UP('geoid')

    # Traffic source
    document_referrer = UP('dr')
    campaign_name = UP('cn')
    campaign_source = UP('cs')
    campaign_medium = UP('cm')
    campaign_keyword = UP('ck')
    campaign_content = UP('cc')
    campaign_id = UP('ci')
    google_adwords_id = UP('gclid')
    google_display_ads_id = UP('dclid')

    # System Info
    screen_resolution = UP('sr')
    viewport_size = UP('vp')
    document_encoding = UP('de')
    screen_colors = UP('sd')
    user_language = UP('ul')
    java_enabled = UP('je')
    flash_version = UP('fl')

    # Content experiments
    experiment_id = UP('xid')
    experiment_variant = UP('xvar')


class PageViewParameters(UrlGenerator):
    location_url = UP('dl')
    host_name = UP('dh')
    path = UP('dp')
    title = UP('dt')
    screen_name = UP('cd')
    link_id = UP('linkid')

    def __init__(self, params=None, location_url=None, host_name=None, path=None, title=None, **kwargs):
        super(PageViewParameters, self).__init__(params=params, location_url=location_url, host_name=host_name,
                                                 path=path, title=title, **kwargs)

    def validate(self):
        super(PageViewParameters, self).validate()
        if not self.location_url and (not self.host_name or not self.path):
            raise InvalidParametersException("Either 'location_url' must be specified, or both 'host_name' and 'path'.")


class AppTrackingParameters(UrlGenerator):
    name = UP('an', True)
    app_id = UP('aid')
    version = UP('av')
    installer_id = UP('aiid')


class EventParameters(UrlGenerator):
    category = UP('ec', True)
    action = UP('ea', True)
    label = UP('el')
    value = UP('ev')

    def __init__(self, category, action=None, label=None, value=None):
        super(EventParameters, self).__init__(category=category, action=action, label=label, value=value)


class AbstractEComUrlGenerator(UrlGenerator):
    transaction_id = UP('ti', True)
    currency_code = UP('cu')

    class Meta(object):
        abstract = True


class EComTransactionParameters(AbstractEComUrlGenerator):
    affiliation = UP('ta')
    revenue = UP('tr')
    shipping = UP('ts')
    tax = UP('tt')


class EComItemParameters(AbstractEComUrlGenerator):
    name = UP('in', True)
    price = UP('ip')
    quantity = UP('iq')
    code = UP('ic')
    category = UP('iv')

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
    sku = UP('id')
    name = UP('nm')
    brand = UP('br')
    category = UP('ca')
    variant = UP('va')
    price = UP('pr')
    quantity = UP('qt')
    coupon_code = UP('cc')
    position = UP('ps')

    class Meta(object):
        item_prefix = 'pr'


class EnhancedEComGeneralParameters(UrlGenerator):
    product_action = UP('pa')
    transaction_id = UP('ti')
    affiliation = UP('ta')
    revenue = UP('tr')
    tax = UP('tt')
    shipping = UP('ts')
    coupon_code = UP('tcc')
    product_action_list = UP('pal')
    checkout_step = UP('cos')
    checkout_step_option = UP('col')
    promotion_action = UP('promoa')


class EnhancedEComPIListParameters(PrefixUrlGenerator):
    name = UP('nm')

    class Meta(object):
        abstract = True
        preset_prefix = 'il'


class EnhancedEComPIProductParameters(EnumeratedUrlGenerator):
    sku = UP('id')
    name = UP('nm')
    brand = UP('br')
    category = UP('ca')
    variant = UP('va')
    position = UP('ps')
    price = UP('pr')

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
    promo_id = UP('id')
    name = UP('nm')
    creative = UP('cr')
    position = UP('ps')

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
    user_timing_label = UP('utl')
    page_load_time = UP('plt')
    dns_time = UP('dns')
    page_download_time = UP('pdt')
    redirect_response_time = UP('rrt')
    tcp_connect_time = UP('tcp')
    server_response_time = UP('srt')
    dom_interactive_time = UP('dit')
    content_load_time = UP('clt')


class ExceptionParameters(UrlGenerator):
    description = UP('exd')
    fatal = UP('exf')

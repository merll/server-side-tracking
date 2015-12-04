# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest

from server_tracking.parameters import VP
from server_tracking.google import HIT_TYPE_EVENT, EECOM_ACTION_PURCHASE
from server_tracking.google.parameters import (GeneralParameters, SessionParameters, InvalidParametersException,
                                               CustomDimensionUrlGenerator, CustomMetricUrlGenerator,
                                               EComTransactionParameters, EComItem, EComItemParameters,
                                               EnhancedEComGeneralParameters, EnhancedEComProductParameters,
                                               EnhancedEComPICustomDimensionProductParameters,
                                               EnhancedEComPIListParameters,
                                               EnhancedEComPICustomMetricProductParameters,
                                               EnhancedEComPIProductParameters)

CLIENT_ID = 42
TRACKING_ID = 'UA-x'


class CustomDimensionParams(CustomDimensionUrlGenerator):
    my_dimension = VP(1)


class CustomMetricParams(CustomMetricUrlGenerator):
    my_metric = VP(2)


class SearchListParams(EnhancedEComPIListParameters):
    class Meta(object):
        index_prefix = 1


class SearchListProductParams(EnhancedEComPIProductParameters):
    class Meta(object):
        index_prefix = 1


class CustomProductDimensionParams(EnhancedEComPICustomDimensionProductParameters):
    class Meta(object):
        index_prefix = 1

    my_dimension = VP(1)


class CustomProductMetricParams(EnhancedEComPICustomMetricProductParameters):
    class Meta(object):
        index_prefix = 1

    my_metric = VP(2)


class UrlGeneratorTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_general_parameters(self):
        gp = GeneralParameters({'tracking_id': TRACKING_ID}, data_source='test', use_cache_buster=True)
        url = gp.url(HIT_TYPE_EVENT)
        self.assertIn('z', url)
        url.pop('z', None)
        self.assertDictEqual(url, {
            'ds': 'test',
            't': HIT_TYPE_EVENT,
            'tid': TRACKING_ID,
            'v': 1,
        })

    def test_session_parameters(self):
        sp = SessionParameters(user_id='1')
        self.assertRaises(InvalidParametersException, sp.url)
        sp.client_id = CLIENT_ID
        url = sp.url()
        self.assertDictEqual(url, {
            'cid': CLIENT_ID,
            'uid': '1',
        })

    def test_custom_parameters(self):
        cd = CustomDimensionParams(my_dimension='test')
        cm = CustomMetricParams()
        cm.my_metric = 101
        self.assertDictEqual(cd.url(), {'cd1': 'test'})
        self.assertDictEqual(cm.url(), {'cm2': 101})

    def test_transaction_parameters(self):
        tp = EComTransactionParameters(transaction_id='1234', revenue=1234.5)
        self.assertDictEqual(tp.url(), {'ti': '1234', 'tr': 1234.5})
        ti = EComItem('item1', price=1000)
        tip = EComItemParameters.from_item(ti, '1234', 'SEK')
        self.assertDictEqual(tip.url(), {'ti': '1234', 'in': 'item1', 'ip': 1000, 'cu': 'SEK'})

    def test_enhanced_transaction_parameters(self):
        tg = EnhancedEComGeneralParameters(product_action=EECOM_ACTION_PURCHASE, transaction_id='1234', revenue=1234.5)
        self.assertDictEqual(tg.url(), {'pa': EECOM_ACTION_PURCHASE, 'ti': '1234', 'tr': 1234.5})
        tp = EnhancedEComProductParameters(sku='xyz', name='item1', price=1000)
        self.assertDictEqual(tp.url(1), {'pr1id': 'xyz', 'pr1nm': 'item1', 'pr1pr': 1000})

    def test_enhanced_product_impression_parameters(self):
        tl = SearchListParams(name='search')
        self.assertDictEqual(tl.url(), {'il1nm': 'search'})
        tlp = SearchListProductParams(sku='xyz', name='item1', price=1000)
        self.assertDictEqual(tlp.url(2), {'il1pi2id': 'xyz', 'il1pi2nm': 'item1', 'il1pi2pr': 1000})
        tlcd = CustomProductDimensionParams(my_dimension='test')
        self.assertDictEqual(tlcd.url(3), {'il1pi3cd1': 'test'})
        tlcm = CustomProductMetricParams(my_metric=101)
        self.assertDictEqual(tlcm.url(4), {'il1pi4cm2': 101})

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest

from server_tracking.utils import anonymize_ip_address, class_from_name


class IpUtilsTest(unittest.TestCase):
    def test_ip4_anonymization(self):
        self.assertEqual(anonymize_ip_address('127.0.0.1'), '127.0.0.0')
        self.assertEqual(anonymize_ip_address('80.90.100.110'), '80.90.100.0')

    def test_ip6_anonymization(self):
        self.assertEqual(anonymize_ip_address('::1'), '::1')
        self.assertEqual(anonymize_ip_address('fe80:0:0:0:200:f8ff:f221:67af'), 'fe80:0000:0000:0000:0000:0000:0000:0000')
        self.assertEqual(anonymize_ip_address('fe80::67af'), 'fe80:0000:0000:0000:0000:0000:0000:0000')
        self.assertEqual(anonymize_ip_address('fe80:abcd:1234:02:23::67af'), 'fe80:abcd:1234:0002:0000:0000:0000:0000')


class GenericUtilsTest(unittest.TestCase):
    def test_class_loader(self):
        self.assertEqual(class_from_name('tests.test_generic_utils.GenericUtilsTest').__name__, self.__class__.__name__)
        self.assertRaises(AttributeError, class_from_name, 'server_tracking.utils')

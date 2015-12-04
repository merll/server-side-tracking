# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import importlib
from itertools import repeat
import re


IP4_REGEX = '((?:\d{1,3}\.){3})\d{1,3}'
IP6_REGEX = '(?:[A-Fa-f0-9]{1,4}::?){1,7}[A-Fa-f0-9]{1,4}'
IP4_PATTERN = re.compile(IP4_REGEX)
IP6_PATTERN = re.compile(IP6_REGEX)


def _expand_groups(address):
    i = 0
    zero_groups = 8 - address.count(':') if '::' in address else 0
    for group in address.split(':'):
        if group:
            i += 1
            if i <= 4:
                yield group.zfill(4)
            else:
                yield '0000'
        elif i > 0:
            i += zero_groups
            for z in repeat('0000', zero_groups):
                yield z
            zero_groups = 1
        else:
            i += 1
            yield '0000'


def anonymize_ip_address(remote_ip):
    m4 = IP4_PATTERN.match(remote_ip)
    if m4:
        return '{0}0'.format(m4.group(1))
    m6 = IP6_PATTERN.match(remote_ip)
    if m6:
        return ':'.join(_expand_groups(remote_ip))
    return remote_ip


def class_from_name(class_path):
    """
    Instantiates a class from the given class path, consisting of a module path and the class name.

    :type class_path: unicode | str
    :return: type
    """
    module_name, __, class_name = class_path.rpartition('.')
    module = importlib.import_module(module_name)
    clazz = getattr(module, class_name)
    if not isinstance(clazz, type):
        raise AttributeError("Module '{0}' has no class '{1}'.", module_name, class_name)
    return clazz

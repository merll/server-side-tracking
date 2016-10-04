# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import six


@six.python_2_unicode_compatible
class InvalidParametersException(Exception):
    @property
    def message(self):
        if self.args:
            if len(self.args) > 1:
                return self.args[0].format(*self.args[1:])
            return self.args[0]
        return None

    def __str__(self):
        return self.message


@six.python_2_unicode_compatible
class SenderException(Exception):
    def __str__(self):
        return ' '.join(self.args) if self.args else ''

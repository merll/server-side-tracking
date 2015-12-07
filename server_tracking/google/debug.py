# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from six import python_2_unicode_compatible

log = logging.getLogger(__name__)

HIT_FIELD_LOG_STR = "%s (Message code: %s, Parameter: %s)"


@python_2_unicode_compatible
class HitParserMessage(object):
    def __init__(self, message_type, description, message_code=None, parameter=None):
        self.message_type = message_type
        self.description = description
        self.message_code = message_code
        self.parameter = parameter

    @classmethod
    def from_dict(cls, d):
        return cls(d['messageType'], d['description'], d.get('messageCode'), d.get('parameter'))

    def __str__(self):
        return '{0.message_type}: {0.description}'.format(self)

    def log(self):
        level = logging.getLevelName(self.message_type)
        if self.message_code or self.parameter:
            log.log(level, HIT_FIELD_LOG_STR, self.description, self.message_code, self.parameter)
        else:
            log.log(level, self.description)


@python_2_unicode_compatible
class HitParserResult(object):
    def __init__(self, valid, hit, messages):
        self.valid = valid
        self.hit = hit
        self.messages = messages

    @classmethod
    def from_dict(cls, d):
        messages = [HitParserMessage.from_dict(msg) for msg in d['parserMessage']]
        return cls(d['valid'], d['hit'], messages)

    def __str__(self):
        status = 'Valid' if self.valid else 'Invalud'
        return '{0} hit: {1}'.format(status, self.hit)

    def log(self):
        if self.valid:
            log.debug("Sent valid hit: %s", self.hit)
        else:
            log.warning("Sent invalid hit: %s.", self.hit)
        for msg in self.messages:
            msg.log()


@python_2_unicode_compatible
class HitParserResults(object):
    def __init__(self, results, messages):
        self.results = results
        self.messages = messages

    @classmethod
    def from_dict(cls, d):
        results = [HitParserResult.from_dict(res) for res in d['hitParsingResult']]
        messages = [HitParserMessage.from_dict(msg) for msg in d['parserMessage']]
        return cls(results, messages)

    def __str__(self):
        return '[{0}]'.format(', '.join(self.results))

    def all_ok(self):
        return all(res.is_valid for res in self.results)

    def log_all(self):
        for msg in self.messages:
            msg.log()
        for res in self.results:
            res.log()


def process_debug_response(response, *args, **kwargs):
    """
    Parses and logs the response from a Google Analytics debug call.

    :param response: Response object.
    :type response: requests.models.Response
    :param args: Misc. args.
    :param kwargs: Misc. kwargs.
    """
    results = HitParserResults.from_dict(response.json(encoding='utf-8'))
    results.log_all()

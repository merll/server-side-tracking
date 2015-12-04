# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

log = logging.getLogger(__name__)

HIT_FIELD_LOG_STR = "%s (Message code: %s, Parameter: %s)"


class HitParserMessage(object):
    def __init__(self, message_type, description, message_code=None, parameter=None):
        self.message_type = message_type
        self.description = description
        self.message_code = message_code
        self.parameter = parameter

    def log(self):
        level = logging.getLevelName(self.message_type)
        if self.message_code or self.parameter:
            log.log(level, HIT_FIELD_LOG_STR, self.description, self.message_code, self.parameter)
        else:
            log.log(level, self.description)

    @classmethod
    def from_dict(cls, d):
        return cls(d['messageType'], d['description'], d.get('messageCode'), d.get('parameter'))


class HitParserResult(object):
    def __init__(self, valid, hit, messages):
        self.valid = valid
        self.hit = hit
        self.messages = messages

    def log(self):
        if self.valid:
            log.debug("Sent valid hit: %s", self.hit)
        else:
            log.warning("Sent invalid hit: %s.", self.hit)
        for msg in self.messages:
            msg.log()

    @classmethod
    def from_dict(cls, d):
        messages = [HitParserMessage.from_dict(msg) for msg in d['parserMessage']]
        return cls(d['valid'], d['hit'], messages)


class HitParserResults(object):
    def __init__(self, results, messages):
        self.results = results
        self.messages = messages

    def all_ok(self):
        return all(res.is_valid for res in self.results)

    def log_all(self):
        for msg in self.messages:
            msg.log()
        for res in self.results:
            res.log()

    @classmethod
    def from_dict(cls, d):
        results = [HitParserResult.from_dict(res) for res in d['hitParsingResult']]
        messages = [HitParserMessage.from_dict(msg) for msg in d['parserMessage']]
        return cls(results, messages)

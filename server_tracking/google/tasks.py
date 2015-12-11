# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from celery import Task, shared_task
from requests import Session, RequestException

from ..settings import update_default_settings, SST_DEFAULT_SETTINGS, GA_DEFAULT_SETTINGS
from .sender import AnalyticsSender
from .parameters import HitParameters


class AnalyticsSendTask(Task):
    abstract = True
    ignore_result = True

    def __init__(self):
        config = self.app.conf
        self.session = session = Session()
        sst_settings = update_default_settings(config, 'SERVER_SIDE_TRACKING', SST_DEFAULT_SETTINGS)
        ga_settings = update_default_settings(config, 'SERVER_SIDE_TRACKING_GA', GA_DEFAULT_SETTINGS)
        self.sender = AnalyticsSender(session,
                                      ssl=ga_settings['ssl'],
                                      debug=sst_settings['debug'],
                                      default_method=sst_settings['send_method'],
                                      post_fallback=sst_settings['post_fallback'],
                                      timeout=sst_settings['timeout'])


@shared_task(bind=True, name='googleanalytics.send_hit', base=AnalyticsSendTask)
def send_hit(self, request_params, timestamp):
    time_queued = datetime.utcfromtimestamp(timestamp)
    time_sent = datetime.utcnow()
    queued_delta = time_sent - time_queued
    request_params.update(HitParameters(queue_time=queued_delta.seconds).url())
    try:
        return self.sender.send(request_params)
    except RequestException as e:
        raise self.retry(exc=e)

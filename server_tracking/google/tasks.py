# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from celery import task
from requests import Session

from .parameters import HitParameters


_session = Session()


def _update_queue_time(request_params, timestamp):
    """

    :param request_params:
    :type request_params: dict
    :param timestamp:
    :type timestamp: int
    :return:
    """
    time_queued = datetime.utcfromtimestamp(timestamp)
    time_sent = datetime.utcnow()
    queued_delta = time_sent - time_queued
    request_params.update(HitParameters(queue_time=queued_delta.seconds).url())


@task(name='googleanalytics.send_get', ignore_result=True)
def send_get(base_url, request_params, timestamp):
    _update_queue_time(request_params, timestamp)
    _session.request('GET', base_url, params=request_params)


@task(name='googleanalytics.send_post', ignore_result=True)
def send_post(base_url, request_data, timestamp):
    _update_queue_time(request_data, timestamp)
    _session.request('POST', base_url, data=request_data)

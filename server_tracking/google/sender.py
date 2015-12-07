# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time
from threading import Thread

from requests import Request, Session

from .. import DEFER_METHOD_THREADED, DEFER_METHOD_CELERY
from . import COLLECT_PATH, DEBUG_PATH, HTTP_URL, SSL_URL
from .debug import process_debug_response


class AnalyticsSender(object):
    """
    Sends predefined data to Google Analytics, either through a ``GET`` or a ``POST``.

    :param session: Session object.
    :type session: requests.sessions.Session
    :param ssl: Use the HTTPS base URL.
    :type ssl: bool
    :param debug: Only debug hits. They are returned with debug information but not processed by GA.
    :type debug: bool
    :param default_method: Default method to use for sending. Default is ``GET``. Change to ``POST`` if you always
     expect large payloads. Otherwise, it is fine leaving ``post_fallback`` set to ``True``.
    :type default_method: unicode | str
    :param post_fallback: If the request size is over 2000 bytes, automatically make a ``POST`` request instead of
     ``GET``.
    :type post_fallback: bool
    :param timeout: Timeout for sending a request, in seconds. Can also be a tuple for specifying connect and read
     timeout separately.
    :type timeout: int | (int, int)
    """
    def __init__(self, session, ssl=True, debug=False, default_method='GET', post_fallback=True, timeout=10):
        self._debug = debug
        self._ssl = True
        base_url = SSL_URL if ssl else HTTP_URL
        if debug:
            self._base_url = '{0}{1}{2}'.format(base_url, DEBUG_PATH, COLLECT_PATH)
            session.hooks['response'].append(process_debug_response)
        else:
            self._base_url = '{0}{1}'.format(base_url, COLLECT_PATH)
        self._session = session
        self._timeout = timeout
        self.send = getattr(self, default_method.lower())
        self._post_fallback = post_fallback

    def get(self, request_params):
        """
        Sends a hit to GA via a GET-request.

        :param request_params: URL parameters.
        :type request_params: dict
        :return: A response object.
        :rtype: requests.models.Response
        """
        req = Request('GET', self._base_url, params=request_params)
        p_req = self._session.prepare_request(req)
        if len(p_req.url) > 2000:
            return self.post(request_params)
        return self._session.send(p_req, timeout=self._timeout)

    def post(self, request_data):
        """
        Sends a hit to GA via a POST-request.

        :param request_data: POST payload.
        :type request_data: dict
        :return: A response object.
        :rtype: requests.models.Response
        """
        return self._session.request('POST', self._base_url, data=request_data, timeout=self._timeout)

    def send(self, request_params):
        """
        Assigned to default method as set during instantiation.
        """
        pass

    @property
    def session(self):
        return self._session


def get_send_function(defer, **kwargs):
    if defer == DEFER_METHOD_CELERY:
        try:
            from .tasks import send_hit
        except ImportError:
            send_hit = None
            raise ValueError("Celery is not available.")
        return lambda request_params: send_hit.apply_async(args=(request_params, time.time()))
    else:
        sender = AnalyticsSender(Session(), **kwargs)
        if defer == DEFER_METHOD_THREADED:
            return lambda request_params: Thread(target=sender.send, args=(request_params, )).start()
        return sender.send

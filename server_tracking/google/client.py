# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from . import (HIT_TYPE_TRANSACTION, HIT_TYPE_TRANSACTION_ITEM, HIT_TYPE_EVENT, HIT_TYPE_SCREENVIEW, HIT_TYPE_PAGEVIEW,
               HIT_TYPE_SOCIAL, HIT_TYPE_TIMING, HIT_TYPE_EXCEPTION)
from .parameters import (GeneralParameters, PageViewParameters, EventParameters, AppTrackingParameters,
                         EComTransactionParameters, EComItemParameters, HitParameters, SessionParameters,
                         SocialInteractionParameters, TimingParameters, ExceptionParameters)


log = logging.getLogger(__name__)


class AnalyticsClient(object):
    """
    Client implementation that uses the Google Analytics Measurement Protocol.

    :param send_func: A function that takes request parameters as input and sends a request to the appropriate URL.
    :type send_func: callable
    :param general_parameters: Default general parameters to pass with each hit.
    :type general_parameters: server_tracking.google.parameters.GeneralParameters | dict
    :param misc_parameters: Additional UrlGenerator objects to use as default parameters.
    :type misc_parameters: tuple[server_tracking.parameters.UrlGenerator] |
     list[server_tracking.parameters.UrlGenerator]
    :param kwargs: Keyword arguments for general parameters.
    """
    def __init__(self, send_func, general_parameters=None, misc_parameters=(), **kwargs):
        if isinstance(general_parameters, (dict, GeneralParameters)):
            self._general_parameters = GeneralParameters(general_parameters)
        elif general_parameters is not None:
            raise ValueError("Invalid type of default parameters: {0}.", type(general_parameters).__name__)
        self._general_parameters.update(kwargs)
        self._misc_parameters = misc_parameters
        self._misc_url = None
        self.update_misc_parameters()
        self._send_func = send_func

    def update_misc_parameters(self):
        """
        Updates the generated parameters from :attr:`AnalyticsClient.misc_parameters`. Only needs to be called
        explicitly, if the objects have gotten modified after the assignment.
        """
        self._misc_url = misc_url = {}
        for p in self._misc_parameters:
            misc_url.update(p.url())

    def request(self, hit_type, *params, **kwargs):
        """
        Sends a request to Google Analytics.

        :param hit_type: Hit type.
        :type hit_type: unicode | str
        :param params: UrlGenerator objects to provide parameters.
        :type params: Tuple[server_tracking.parameters.UrlGenerator]
        :param kwargs: Raw url parameters to update the generated url with.
        :return: In normal scenarios always returns ``True``. For synchronous requests actually processes the status
         code, but Google Analytics does not return error codes for invalid hits. In debug mode, hits are validated
         by GA and this method returns the parsed result.
        :rtype: bool | server_tracking.google.debug.HitParserResults
        """
        request_params = self._general_parameters.url(hit_type)
        for p in params:
            if p:
                request_params.update(p.url())
        request_params.update(self._misc_url)
        request_params.update(kwargs)
        response = self._send_func(request_params)
        if response:
            return response.status_code <= 400
        return True

    def pageview(self, params=None, location_url=None, host_name=None, path=None, session_params=None, misc_params=(),
                 **kwargs):
        """
        Generates and sends a page view.

        :param params: Initial page view parameters. Where applicable, overridden by following arguments.
        :type params: dict | server_tracking.google.parameters.PageViewParameters
        :param location_url: Full location URL.
        :type location_url: unicode | str
        :param host_name: Host name.
        :type host_name: unicode | str
        :param path: URL path.
        :type path: unicode | str
        :param session_params: Optional session parameters.
        :type session_params: server_tracking.google.parameters.SessionParameters
        :param misc_params: Miscellaneous parameters to add to the hit.
        :type misc_params: tuple[server_tracking.parameters.UrlGenerator]
        :param kwargs: Raw url parameters to update the generated url with.
        :return: Varies, see :meth:`request`.
        :rtype: bool | unicode | str
        """
        page = PageViewParameters(params,
                                  location_url=location_url,
                                  host_name=host_name,
                                  path=path,
                                  **kwargs)
        return self.request(HIT_TYPE_PAGEVIEW, page, session_params, *misc_params)

    def screenview(self, screen_name, app_name, page_params=None, misc_params=(), **kwargs):
        """
        Generates and sends a screen view.

        :param screen_name: Screen name.
        :type screen_name: unicode | str
        :param app_name: App name.
        :type app_name: unicode | str
        :param page_params: Optional additional page view parameters.
        :type page_params: dict | server_tracking.google.parameters.PageViewParameters
        :param misc_params: Miscellaneous parameters to add to the hit.
        :type misc_params: tuple[server_tracking.parameters.UrlGenerator]
        :param kwargs: Raw url parameters to update the generated url with.
        :return: Varies, see :meth:`request`.
        :rtype: bool | unicode | str
        """
        page = PageViewParameters(page_params, screen_name=screen_name)
        app = AppTrackingParameters(name=app_name, **kwargs)
        return self.request(HIT_TYPE_SCREENVIEW, page, app, *misc_params)

    def event(self, category, action, label=None, value=None, location_url=None, host_name=None, path=None,
              non_interaction_hit=None, page_params=None, session_params=None, hit_params=None, misc_params=(),
              **kwargs):
        """
        Generates and sends an event.

        :param category: Event category.
        :type category: unicode | str
        :param action: Event action.
        :type action: unicode | str
        :param label: Event label.
        :type label: unicode | str
        :param value: Event value.
        :type value: int | float
        :param location_url: Location URL. Alternative to providing ``host_name`` and ``path``.
        :type location_url: unicode | str
        :param host_name: Host name.
        :type host_name: unicode | str
        :param path: URL path.
        :type path: unicode | str
        :param non_interaction_hit: Set to ``1`` if event is not based on a user interaction.
        :type non_interaction_hit: int
        :param page_params: Page view parameters. Where provided, updated with previous parameters ``location_url``,
         ``host_name``, and ``path``.
        :param session_params: Optional session parameters.
        :type session_params: server_tracking.google.parameters.SessionParameters
        :param hit_params: Optional hit parameters. Where provided, updated with previous parameter
         ``non_interaction_hit``.
        :type hit_params: server_tracking.google.parameters.HitParameters
        :param misc_params: Miscellaneous parameters to add to the hit.
        :type misc_params: tuple[server_tracking.parameters.UrlGenerator]
        :param kwargs: Raw url parameters to update the generated url with.
        :return: Varies, see :meth:`request`.
        :rtype: bool | unicode | str
        """
        page = PageViewParameters(page_params, location_url=location_url, host_name=host_name, path=path)
        event = EventParameters(category, action=action, label=label, value=value)
        session = SessionParameters(session_params)
        hit = HitParameters(hit_params, non_interaction_hit=non_interaction_hit)
        return self.request(HIT_TYPE_EVENT, page, event, session, hit, *misc_params, **kwargs)

    def transaction(self, transaction_id, items, affiliation=None, revenue='sum', shipping=None, tax=None,
                    currency_code=None, page_params=None, misc_params=(), **kwargs):
        """
        Sends an E-Commerce transaction and items.

        :param transaction_id: Transaction id.
        :type transaction_id: int | unicode | str
        :param items: List of items in the transaction.
        :type items: list[server_tracking.google.parameters.EComItem]
        :param affiliation: Transaction affiliation.
        :type affiliation: unicode | str
        :param revenue: Transaction revenue. Pass ``sum`` if this is the sum of each item ``price * quantity`` plus
         ``shipping`` and ``tax``.
        :type revenue: float | unicode | str
        :param shipping: Transaction shipping.
        :type shipping: float
        :param tax: Transaction tax.
        :type tax: float
        :param currency_code: Transaction currency code. Also applied to all items that do not have one on their own.
        :type currency_code: unicode | str
        :param page_params: Page view parameters.
        :type page_params: server_tracking.google.parameters.PageViewParameters | dict
        :param misc_params: Miscellaneous parameters to add to the hit.
        :type misc_params: tuple[server_tracking.parameters.UrlGenerator]
        :param kwargs: Raw url parameters to update the generated url with.
        :return: Returns ``True`` when all generated hits got sent or deferred to a separate thread / task.
        :rtype: bool
        """
        page = PageViewParameters(page_params)
        if revenue == 'sum':
            revenue = shipping or 0 + tax or 0 + sum((item.price or 0) * (item.quantity or 1) for item in items)
        transaction = EComTransactionParameters(transaction_id=transaction_id, affiliation=affiliation, revenue=revenue,
                                                shipping=shipping, tax=tax, **kwargs)
        item_params = [EComItemParameters.from_item(item, transaction_id, transaction_currency=currency_code)
                       for item in items]
        tr = self.request(HIT_TYPE_TRANSACTION, transaction, page, *misc_params)
        ti = all(self.request(HIT_TYPE_TRANSACTION_ITEM, item, page) for item in item_params) if item_params else True
        return tr and ti

    def social(self, network, action, target, page_params=None, misc_params=(), **kwargs):
        """
        Sends a social interaction hit.

        :param network: Social network.
        :type network: unicode | str
        :param action: Social action.
        :type action: unicode | str
        :param target: Social action target, e.g. URL.
        :type target: unicode | str
        :param page_params: Page view parameters.
        :type page_params: server_tracking.google.parameters.PageViewParameters | dict
        :param misc_params: Miscellaneous parameters to add to the hit.
        :type misc_params: tuple[server_tracking.parameters.UrlGenerator]
        :param kwargs: Raw url parameters to update the generated url with.
        :return: Varies, see :meth:`request`.
        :rtype: bool | unicode | str
        """
        social = SocialInteractionParameters(network=network, action=action, target=target)
        page = PageViewParameters(page_params) if page_params else None
        return self.request(HIT_TYPE_SOCIAL, social, page, *misc_params, **kwargs)

    def timing(self, user_timing_category, user_timing_variable, user_timing_value, page_params=None, misc_params=(),
               **kwargs):
        """
        Generates and sends a timing event.

        :param user_timing_category: User timing category.
        :param user_timing_variable: User timing variable.
        :param user_timing_value: User timing value.
        :param page_params: Page view parameters.
        :type page_params: server_tracking.google.parameters.PageViewParameters | dict
        :param misc_params: Miscellaneous parameters to add to the hit.
        :type misc_params: tuple[server_tracking.parameters.UrlGenerator]
        :param kwargs: Raw url parameters to update the generated url with.
        :return: Varies, see :meth:`request`.
        :rtype: bool | unicode | str
        """
        timing = TimingParameters(user_timing_category=user_timing_category, user_timing_variable=user_timing_variable,
                                  user_timing_value=user_timing_value)
        page = PageViewParameters(page_params) if page_params else None
        return self.request(HIT_TYPE_TIMING, timing, page, *misc_params, **kwargs)

    def exception(self, description=None, fatal=None, page_params=None, misc_params=(), **kwargs):
        """
        Sends an exception hit.

        :param description: Exception description.
        :type description: unicode | str
        :param fatal: Set to ``True`` if the exception was fatal.
        :type fatal: int
        :param page_params: Page view parameters.
        :type page_params: server_tracking.google.parameters.PageViewParameters | dict
        :param misc_params: Miscellaneous parameters to add to the hit.
        :type misc_params: tuple[server_tracking.parameters.UrlGenerator]
        :param kwargs: Raw url parameters to update the generated url with.
        :return: Varies, see :meth:`request`.
        :rtype: bool | unicode | str
        """
        if description or fatal is not None:
            exception = ExceptionParameters(description=description, fatal=fatal)
        else:
            exception = None
        page = PageViewParameters(page_params) if page_params else None
        return self.request(HIT_TYPE_EXCEPTION, exception, page, *misc_params, **kwargs)

    @property
    def general_parameters(self):
        """
        General parameters to be sent with every hit, e.g. page view or event.

        :return: GeneralParameters object. Input can also be provided as a dictionary.
        :rtype: server_tracking.google.parameters.GeneralParameters
        """
        return self._general_parameters

    @general_parameters.setter
    def general_parameters(self, value):
        self._general_parameters = GeneralParameters(value)

    @property
    def misc_parameters(self):
        """
        Miscellaneous parameters to be sent with every hit, e.g. page view or event. Can for example include
        a :class:`server_tracking.google.parameters.SessionParameters` object, if you repeatedly send in data from the
        same client.

        :return: Parameter objects.
        :rtype: tuple[server_tracking.parameters.UrlGenerator] | list[server_tracking.parameters.UrlGenerator]
        """
        return self._misc_parameters

    @misc_parameters.setter
    def misc_parameters(self, value):
        self._misc_parameters = value
        self.update_misc_parameters()

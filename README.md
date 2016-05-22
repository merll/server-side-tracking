# server-side-tracking

Server-side tracking in Google Analytics for web applications.

This library provides an implementation for the full set of URL parameters to the Google Analytics Measurement Protocol.
Further tracking systems can be implemented using the url generator framework.

Hits can be sent synchronously, via a separate thread, or through a Celery task.

An app for integration into Django is also included, for extracting all available parameters from the request. It can be
used via a middleware or a view mixin class. Events can be tracked through a method decorator.

# Advantages of server-side tracking

Generally client-side tracking is subject to several reliability issues. One reason is that browsers may block all or
portions of the tracking code, and therefore not send any data. It can also happen that clients may send spam or
manipulated data. This is an even larger problem, since it is hardly possible to determine which requests are fabricated
or altered. Neither is it possible to add significant security beforehand, as all information for tracking has to be
exposed to the client side somehow.

Server-side tracking allows for controlling exactly what data is sent, without even exposing credentials, account
numbers, etc. Additionally, sensitive client-side data can already be filtered before it is sent to the third-party
service.

# Respecting privacy during collection 

This library was developed with the intention of gathering useful site usage data while respecting privacy concerns.

* By default, only session-based cookies are set by the server.
* Cookies are only stored permanently, if the client has sent an explicit acceptance.
* Personal identifiable information, such as IP addresses are anonymized before they are sent to a third party.
* The generated client-id is entirely random, and by default set with an `HttpOnly` flag, which prevents submission
  to any other system by scripts.

While I cannot make any guarantees, some functionality is added for supporting a EU-law compliant tracking solution.
I would like to emphasize however that it is the responsibility of the developer implementing server-side tracking to
do this in compliance with applicable law and the terms of service of the tracking product (e.g. Google Analytics).

Within the EU for example, appropriate information needs to be shown to website users about tracking (e.g. notification
pop-up, cookie policy) and their consent is required prior to storing information. These client-side elements are out
of scope for this library. Additionally, Google does not permit submission of any personal identity information such as
names and email addresses.

Generally I discourage implementing any tracking - server- or client-side - without any user information or with the
purpose of circumventing client-side privacy protection software.

# Implementation

The implementation is currently prepared mainly for Django apps.

## Basic settings

Add the following lines to your settings module:

    SERVER_SIDE_TRACKING_GA = {
        'property': 'UA-xxxxxxxx-x',  # Add your property id here.
    }

## Middleware

In order to track every page view (excluding AJAX), the middleware can be set up through the settings.

    MIDDLEWARE_CLASSES = (
        ... # default middelware classes
        'server_tracking.django.middleware.PageViewMiddleware',
    )

## Mixin

You can add `server_tracking.django.mixins.PageViewMixin` to your class view implementation, for tracking requests to
that view.


## Exclusions

URL path prefixes can be excluded from the aforementioned methods by setting `pageview_exclude` in the settings:

    SERVER_SIDE_TRACKING = {
        ...
        'pageview_exclude': (
            'admin/',
        ),
        ...
    }
    
This example replicates the default setting.

## Decorator

A decorator can be used for tracking events:

    class TransactionView(View):
        @track_event('Transaction', 'Get')
        def get(self, request):
            ...

## Custom

Tracking hits can be built entirely from scratch. However, in order to generate all data which is available by default,
there are a few helper functions:

    server_tracking.django.utils.get_default_parameters

extracts all available data from the request object. It also update the session id as necessary.

    server_tracking.django.utils.get_title
    
attempts to extract the page title using multiple methods. More can be configured in the setting
`django_title_extractors`. The default is

    SERVER_SIDE_TRACKING = {
        ...
        'django_title_extractors': (
            'server_tracking.django.utils.ContextTitleExtractor',
            'server_tracking.django.utils.ViewTitleExtractor',
        ),
        ...
    }


# Pending

* Comprehensive documentation.
* Enhanced E-Commerce utilities (url generators are implemented, but usage is quite manual).
* More app server / framework integrations.

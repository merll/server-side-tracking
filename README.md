# server-tracking

Server-side tracking in Google Analytics for web applications.

This library provides an implementation for the full set of URL parameters to the Google Analytics Measurement Protocol.
Further tracking systems can be implemented using the url generator framework.

Hits can be sent synchronously, via a separate thread, or through a Celery tasks.

An app for integration into Django is also included, for extracting all available parameters from the request. It can be
used via a middleware or a view mixin class. Events can be tracked via a method decorator.

Pending:

* Better overview in README and comprehensive documentation.
* Enhanced E-Commerce utilities (url generators are implemented, but usage is quite manual).
* More app server / framework integrations.

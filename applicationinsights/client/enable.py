import sys

from applicationinsights import TelemetryClient
from applicationinsights.channel import SynchronousSender, SynchronousQueue, TelemetryChannel

import time

current_milli_time = lambda: int(round(time.time() * 1000))


def _track_dependency(tc, always_flush, host, method, url, duration, response_code):
    success = response_code < 400

    tc.track_dependency(
        name=host,
        data="{} {}".format(method, url),
        target=url,
        duration=duration,
        success=success,
        result_code=response_code
    )

    if always_flush:
        tc.flush()


def __enable_for_urllib3(http_connection_pool_class, https_connection_pool_class, instrumentation_key,
                         telemetry_channel, always_flush):
    if not instrumentation_key:
        raise Exception('Instrumentation key was required but not provided')

    if telemetry_channel is None:
        sender = SynchronousSender()
        queue = SynchronousQueue(sender)
        telemetry_channel = TelemetryChannel(None, queue)

    client = TelemetryClient(instrumentation_key, telemetry_channel)

    orig_http_urlopen_method = http_connection_pool_class.urlopen
    orig_https_urlopen_method = https_connection_pool_class.urlopen

    def custom_urlopen_wrapper(urlopen_func):
        def custom_urlopen(*args, **kwargs):
            start_time = current_milli_time()
            response = urlopen_func(*args, **kwargs)
            try:  # make sure to always return the response
                duration = current_milli_time() - start_time
                try:
                    method = args[1]
                except IndexError:
                    method = kwargs['method']

                try:
                    url = args[2]
                except IndexError:
                    url = kwargs['url']

                _track_dependency(client, always_flush, args[0].host, method, url, duration, response.status)
            finally:
                return response

        return custom_urlopen

    http_connection_pool_class.urlopen = custom_urlopen_wrapper(orig_http_urlopen_method)
    https_connection_pool_class.urlopen = custom_urlopen_wrapper(orig_https_urlopen_method)


def enable_for_urllib3(instrumentation_key, telemetry_channel=None, always_flush=False):
    """Enables the automatic collection of dependency telemetries for HTTP calls with urllib3.

    .. code:: python

        from applicationinsights.client import enable_for_urllib3
        import urllib3.requests

        enable_for_urllib3('<YOUR INSTRUMENTATION KEY GOES HERE>')

        urllib3.PoolManager().request("GET", "https://www.python.org/")
        # a dependency telemetry will be sent to the Application Insights service

    Args:
        instrumentation_key (str). the instrumentation key to use while sending telemetry to the service.
        telemetry_channel (TelemetryChannel). a custom telemetry channel to use
        always_flush (bool). if true every HTTP call will flush the dependency telemetry
    """
    from urllib3.connectionpool import HTTPConnectionPool, HTTPSConnectionPool
    __enable_for_urllib3(HTTPConnectionPool, HTTPSConnectionPool, instrumentation_key, telemetry_channel, always_flush)


def enable_for_requests(instrumentation_key, telemetry_channel=None, always_flush=False):
    """Enables the automatic collection of dependency telemetries for HTTP calls with requests.

    .. code:: python

        from applicationinsights.client import enable_for_requests
        import requests

        enable_for_requests('<YOUR INSTRUMENTATION KEY GOES HERE>')

        requests.get("https://www.python.org/")
        # a dependency telemetry will be sent to the Application Insights service

    Args:
        instrumentation_key (str). the instrumentation key to use while sending telemetry to the service.
        telemetry_channel (TelemetryChannel). a custom telemetry channel to use
        always_flush (bool). if true every HTTP call will flush the dependency telemetry
    """
    from requests.packages.urllib3.connectionpool import HTTPConnectionPool, HTTPSConnectionPool
    __enable_for_urllib3(HTTPConnectionPool, HTTPSConnectionPool, instrumentation_key, telemetry_channel, always_flush)


def _track_for_urllib(tc, always_flush, start_time, req, resp):
    duration = current_milli_time() - start_time
    method = req.get_method()

    if sys.version_info.major > 2:
        url = req.selector
        status = resp.status
    else:
        url = req.get_selector()
        status = resp.code

    _track_dependency(tc, always_flush, req.host, method, url, duration, status)


def __enable_for_urllib(base_http_handler_class, base_https_handler_class, instrumentation_key, telemetry_channel=None,
                        always_flush=False):
    pass
    if not instrumentation_key:
        raise Exception('Instrumentation key was required but not provided')

    if telemetry_channel is None:
        sender = SynchronousSender()
        queue = SynchronousQueue(sender)
        telemetry_channel = TelemetryChannel(None, queue)

    client = TelemetryClient(instrumentation_key, telemetry_channel)

    class AppInsightsHTTPHandler(base_http_handler_class, object):
        def http_open(self, req):
            start_time = current_milli_time()
            response = super(AppInsightsHTTPHandler, self).http_open(req)

            try:
                _track_for_urllib(client, always_flush, start_time, req, response)
            finally:
                return response

    class AppInsightsHTTPSHandler(base_https_handler_class, object):
        def https_open(self, req):
            start_time = current_milli_time()
            response = super(AppInsightsHTTPSHandler, self).https_open(req)

            try:
                _track_for_urllib(client, always_flush, start_time, req, response)
            finally:
                return response

    return AppInsightsHTTPHandler, AppInsightsHTTPSHandler


def enable_for_urllib(instrumentation_key, telemetry_channel=None, always_flush=False):
    """Enables the automatic collection of dependency telemetries for HTTP calls with urllib.

    .. code:: python

        from applicationinsights.client import enable_for_urllib
        import urllib.requests

        enable_for_urllib('<YOUR INSTRUMENTATION KEY GOES HERE>')

        urllib.request.urlopen("https://www.python.org/")
        # a dependency telemetry will be sent to the Application Insights service

    Args:
        instrumentation_key (str). the instrumentation key to use while sending telemetry to the service.
        telemetry_channel (TelemetryChannel). a custom telemetry channel to use
        always_flush (bool). if true every HTTP call will flush the dependency telemetry
    """
    import urllib.request

    http_handler, https_handler = __enable_for_urllib(
        urllib.request.HTTPHandler,
        urllib.request.HTTPSHandler,
        instrumentation_key,
        telemetry_channel,
        always_flush
    )

    urllib.request.install_opener(
        urllib.request.build_opener(http_handler, https_handler)
    )


def enable_for_urllib2(instrumentation_key, telemetry_channel=None, always_flush=False):
    """Enables the automatic collection of dependency telemetries for HTTP calls with urllib2.

    .. code:: python

        from applicationinsights.client import enable_for_urllib2
        import urllib2

        enable_for_urllib2('<YOUR INSTRUMENTATION KEY GOES HERE>')

        urllib2.urlopen("https://www.python.org/")
        # a dependency telemetry will be sent to the Application Insights service

    Args:
        instrumentation_key (str). the instrumentation key to use while sending telemetry to the service.
        telemetry_channel (TelemetryChannel). a custom telemetry channel to use
        always_flush (bool). if true every HTTP call will flush the dependency telemetry
    """
    import urllib2

    http_handler, https_handler = __enable_for_urllib(
        urllib2.HTTPHandler,
        urllib2.HTTPSHandler,
        instrumentation_key,
        telemetry_channel,
        always_flush
    )
    urllib2.install_opener(
        urllib2.build_opener(http_handler, https_handler)
    )

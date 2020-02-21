import sys

from applicationinsights import TelemetryClient
from applicationinsights.channel import AsynchronousSender, AsynchronousQueue, TelemetryChannel

import time

current_milli_time = lambda: int(round(time.time() * 1000))


def enable_all(*args, **kwargs):
    enable_for_requests(*args, **kwargs)
    enable_for_urllib3(*args, **kwargs)

    if sys.version_info.major > 2:
        enable_for_urllib(*args, **kwargs)
    else:
        enable_for_urllib2(*args, **kwargs)


def __enable_for_urllib3(http_connection_pool_class, https_connection_pool_class, instrumentation_key, telemetry_channel, always_flush):
    if not instrumentation_key:
        raise Exception('Instrumentation key was required but not provided')

    if telemetry_channel is None:
        sender = AsynchronousSender()
        queue = AsynchronousQueue(sender)
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

                success = response.status < 400

                client.track_dependency(args[0].host, "{} {}".format(method, url), target=url, duration=duration,
                                        success=success, result_code=response.status)
                if always_flush:
                    client.flush()
            finally:
                return response

        return custom_urlopen

    http_connection_pool_class.urlopen = custom_urlopen_wrapper(orig_http_urlopen_method)
    https_connection_pool_class.urlopen = custom_urlopen_wrapper(orig_https_urlopen_method)


def enable_for_urllib3(instrumentation_key, telemetry_channel=None, always_flush=False):
    from urllib3.connectionpool import HTTPConnectionPool, HTTPSConnectionPool
    __enable_for_urllib3(HTTPConnectionPool, HTTPSConnectionPool, instrumentation_key, telemetry_channel, always_flush)


def enable_for_requests(instrumentation_key, telemetry_channel=None, always_flush=False):
    from requests.packages.urllib3.connectionpool import HTTPConnectionPool, HTTPSConnectionPool
    __enable_for_urllib3(HTTPConnectionPool, HTTPSConnectionPool, instrumentation_key, telemetry_channel, always_flush)


def __enable_for_urllib(base_http_handler_class, base_https_handler_class, instrumentation_key, telemetry_channel=None, always_flush=False):
    pass
    if not instrumentation_key:
        raise Exception('Instrumentation key was required but not provided')

    if telemetry_channel is None:
        sender = AsynchronousSender()
        queue = AsynchronousQueue(sender)
        telemetry_channel = TelemetryChannel(None, queue)

    client = TelemetryClient(instrumentation_key, telemetry_channel)

    class AppInsightsHTTPHandler(base_http_handler_class, object):
        def http_open(self, req):
            start_time = current_milli_time()
            response = super(AppInsightsHTTPHandler, self).http_open(req)

            try:
                duration = current_milli_time() - start_time
                method = req.get_method()

                if sys.version_info.major > 2:
                    url = req.selector
                    status = response.status
                else:
                    url = req.get_selector()
                    status = response.code

                success = status < 400

                client.track_dependency(req.host, "{} {}".format(method, url), target=url, duration=duration,
                                        success=success, result_code=status)
                if always_flush:
                    client.flush()
            finally:
                return response

    class AppInsightsHTTPSHandler(base_https_handler_class, object):
        def https_open(self, req):
            start_time = current_milli_time()
            response = super(AppInsightsHTTPSHandler, self).https_open(req)

            try:
                duration = current_milli_time() - start_time
                method = req.get_method()

                if sys.version_info.major > 2:
                    url = req.selector
                    status = response.status
                else:
                    url = req.get_selector()
                    status = response.code

                success = status < 400

                client.track_dependency(req.host, "{} {}".format(method, url), target=url, duration=duration,
                                        success=success, result_code=status)
                if always_flush:
                    client.flush()
            finally:
                return response

    return AppInsightsHTTPHandler, AppInsightsHTTPSHandler


def enable_for_urllib(instrumentation_key, telemetry_channel=None, always_flush=False):
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



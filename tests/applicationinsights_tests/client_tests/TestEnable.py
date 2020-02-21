import json

from applicationinsights import channel, client
import unittest

import httpretty
import requests
import urllib3

import os.path
import sys

from tests.applicationinsights_tests.common import MockSynchronousSender

rootDirectory = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '..', '..')
if rootDirectory not in sys.path:
    sys.path.append(rootDirectory)

BASE_HOST = "test.com"
BASE_URL = "/test"
BASE_HTTP_URL = "http://{}{}".format(BASE_HOST, BASE_URL)
BASE_HTTPS_URL = "https://{}{}".format(BASE_HOST, BASE_URL)


class TestEnable(unittest.TestCase):
    @httpretty.activate
    def test_enable_for_requests(self):
        sender = MockSynchronousSender()
        queue = channel.SynchronousQueue(sender)
        telemetry_channel = channel.TelemetryChannel(None, queue)
        telemetry_channel.context.properties["foo"] = "bar"
        telemetry_channel.context.operation.id = 1001

        client.enable_for_requests('foo', telemetry_channel=telemetry_channel, always_flush=True)

        httpretty.register_uri(
            httpretty.GET,
            BASE_HTTP_URL,
            body='{"foo": "bar"}'
        )

        httpretty.register_uri(
            httpretty.GET,
            BASE_HTTPS_URL,
            body='{"foo": "bar"}'
        )

        for url in [BASE_HTTP_URL, BASE_HTTPS_URL]:
            response = requests.get(url)
            self.assertEqual(200, response.status_code)
            self.assertEqual({"foo": "bar"}, response.json())

        self.assertEqual(2, len(sender.data))

        for i in range(2):
            data = sender.data[i][0]
            self.assertIsNotNone(data)
            self.assertEqual('foo', data.ikey)
            self.assertEqual('Microsoft.ApplicationInsights.RemoteDependency', data.name)
            self.assertEqual('bar', data.data.base_data.properties['foo'])
            self.assertEqual('GET /test', data.data.base_data.data)
            self.assertEqual('/test', data.data.base_data.target)
            self.assertEqual('200', data.data.base_data.result_code)
            self.assertEqual(1001, data.tags.get('ai.operation.id'))

    def test_enable_for_requests_raises_exception_on_no_instrumentation_key(self):
        self.assertRaises(Exception, client.enable_for_requests)

    @httpretty.activate
    def test_enable_for_urllib3(self):
        sender = MockSynchronousSender()
        queue = channel.SynchronousQueue(sender)
        telemetry_channel = channel.TelemetryChannel(None, queue)
        telemetry_channel.context.properties["foo"] = "bar"
        telemetry_channel.context.operation.id = 1001

        client.enable_for_urllib3('foo', telemetry_channel=telemetry_channel, always_flush=True)

        httpretty.register_uri(
            httpretty.GET,
            BASE_HTTP_URL,
            body='{"foo": "bar"}'
        )

        httpretty.register_uri(
            httpretty.GET,
            BASE_HTTPS_URL,
            body='{"foo": "bar"}'
        )

        for url in [BASE_HTTP_URL, BASE_HTTPS_URL]:
            response = urllib3.PoolManager().request("GET", url)
            self.assertEqual(200, response.status)
            self.assertEqual({"foo": "bar"}, json.loads(response.data.decode('utf-8')))

        self.assertEqual(2, len(sender.data))

        for i in range(2):
            data = sender.data[i][0]
            self.assertIsNotNone(data)
            self.assertEqual('foo', data.ikey)
            self.assertEqual('Microsoft.ApplicationInsights.RemoteDependency', data.name)
            self.assertEqual('bar', data.data.base_data.properties['foo'])
            self.assertEqual('GET /test', data.data.base_data.data)
            self.assertEqual('/test', data.data.base_data.target)
            self.assertEqual('200', data.data.base_data.result_code)
            self.assertEqual(1001, data.tags.get('ai.operation.id'))

    def test_enable_for_urllib3_raises_exception_on_no_instrumentation_key(self):
        self.assertRaises(Exception, client.enable_for_urllib3)

    @httpretty.activate
    @unittest.skipIf(sys.version_info.major < 3, "Not relevant for Python 2")
    def test_enable_for_urllib(self):
        import urllib.request

        sender = MockSynchronousSender()
        queue = channel.SynchronousQueue(sender)
        telemetry_channel = channel.TelemetryChannel(None, queue)
        telemetry_channel.context.properties["foo"] = "bar"
        telemetry_channel.context.operation.id = 1001

        client.enable_for_urllib('foo', telemetry_channel=telemetry_channel, always_flush=True)

        httpretty.register_uri(
            httpretty.GET,
            BASE_HTTP_URL,
            body='{"foo": "bar"}'
        )

        httpretty.register_uri(
            httpretty.GET,
            BASE_HTTPS_URL,
            body='{"foo": "bar"}'
        )

        for url in [BASE_HTTP_URL, BASE_HTTPS_URL]:
            response = urllib.request.urlopen(url)
            self.assertEqual(200, response.status)
            self.assertEqual({"foo": "bar"}, json.loads(response.read().decode('utf-8')))

        self.assertEqual(2, len(sender.data))

        for i in range(2):
            data = sender.data[i][0]
            self.assertIsNotNone(data)
            self.assertEqual('foo', data.ikey)
            self.assertEqual('Microsoft.ApplicationInsights.RemoteDependency', data.name)
            self.assertEqual('bar', data.data.base_data.properties['foo'])
            self.assertEqual('GET /test', data.data.base_data.data)
            self.assertEqual('/test', data.data.base_data.target)
            self.assertEqual('200', data.data.base_data.result_code)
            self.assertEqual(1001, data.tags.get('ai.operation.id'))

    def test_enable_for_urllib_raises_exception_on_no_instrumentation_key(self):
        self.assertRaises(Exception, client.enable_for_urllib)

    @httpretty.activate
    @unittest.skipIf(sys.version_info.major > 2, "Not relevant for Python 3")
    def test_enable_for_urllib2(self):
        import urllib2

        sender = MockSynchronousSender()
        queue = channel.SynchronousQueue(sender)
        telemetry_channel = channel.TelemetryChannel(None, queue)
        telemetry_channel.context.properties["foo"] = "bar"
        telemetry_channel.context.operation.id = 1001

        client.enable_for_urllib2('foo', telemetry_channel=telemetry_channel, always_flush=True)

        httpretty.register_uri(
            httpretty.GET,
            BASE_HTTP_URL,
            body='{"foo": "bar"}'
        )

        httpretty.register_uri(
            httpretty.GET,
            BASE_HTTPS_URL,
            body='{"foo": "bar"}'
        )

        for url in [BASE_HTTP_URL, BASE_HTTPS_URL]:
            response = urllib2.urlopen(url)
            self.assertEqual(200, response.code)
            self.assertEqual({"foo": "bar"}, json.loads(response.read().decode('utf-8')))

        self.assertEqual(2, len(sender.data))

        for i in range(2):
            data = sender.data[i][0]
            self.assertIsNotNone(data)
            self.assertEqual('foo', data.ikey)
            self.assertEqual('Microsoft.ApplicationInsights.RemoteDependency', data.name)
            self.assertEqual('bar', data.data.base_data.properties['foo'])
            self.assertEqual('GET /test', data.data.base_data.data)
            self.assertEqual('/test', data.data.base_data.target)
            self.assertEqual('200', data.data.base_data.result_code)
            self.assertEqual(1001, data.tags.get('ai.operation.id'))

    def test_enable_for_urllib2_raises_exception_on_no_instrumentation_key(self):
        self.assertRaises(Exception, client.enable_for_urllib2)

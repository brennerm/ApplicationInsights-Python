import json

from applicationinsights import channel, client
import unittest

import httpretty
import requests
import urllib3

import sys
import os.path

from tests.applicationinsights_tests.common import MockSynchronousSender

rootDirectory = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '..', '..')
if rootDirectory not in sys.path:
    sys.path.append(rootDirectory)

BASE_HTTP_URL = "http://test.com/test"
BASE_HTTPS_URL = "https://test.com/test"


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

        assert requests.get(BASE_HTTP_URL).json() == {"foo": "bar"}
        assert requests.get(BASE_HTTPS_URL).json() == {"foo": "bar"}

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

        assert json.loads(urllib3.PoolManager().request("GET", BASE_HTTP_URL).data) == {"foo": "bar"}
        assert json.loads(urllib3.PoolManager().request("GET", BASE_HTTPS_URL).data) == {"foo": "bar"}

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

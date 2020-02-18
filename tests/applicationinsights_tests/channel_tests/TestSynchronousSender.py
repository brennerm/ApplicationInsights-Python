from applicationinsights import channel
import unittest

import sys
import os.path
rootDirectory = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '..', '..')
if rootDirectory not in sys.path:
    sys.path.append(rootDirectory)


class TestSynchronousSender(unittest.TestCase):
    def test_construct(self):
        sender = channel.SynchronousSender()
        self.assertEqual(
            'https://dc.services.visualstudio.com/v2/track', sender.service_endpoint_uri)

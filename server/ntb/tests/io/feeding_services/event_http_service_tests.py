import os
from unittest import mock

from superdesk.io.feeding_services import http_base_service
from planning.feeding_services import event_http_service
from planning.tests import TestCase


class MockResponse:
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content
        self.headers = mock.MagicMock()


class EventHTTPFeedingServiceTestCase(TestCase):

    def setUp(self):
        super().setUp()

    @mock.patch.object(http_base_service, 'requests')
    def test_update_ntb(self, requests):
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(os.path.join(dirname, '../fixtures', 'ntb_event.xml'))

        with open(fixture, 'rb') as f:
            response = MockResponse(status_code=200, content=f.read())
            response.ok = True
            requests.get.return_value = response

        service = event_http_service.EventHTTPFeedingService()
        provider = {
            'feed_parser': 'ntb_event_xml',
            'config': {
                'url': 'https://example.com/NTBEvent.xml',
            },
            'is_closed': False,
            '_id': 'ntb_event_xml',
            'name': 'ntb_event_xml',
        }

        events = list(service.update(provider, {}))
        self.assertEqual(len(events), 1)

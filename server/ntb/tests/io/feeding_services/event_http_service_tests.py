import os
import responses

from planning.tests import TestCase
from planning.feeding_services import event_http_service


class EventHTTPFeedingServiceTestCase(TestCase):
    @responses.activate(assert_all_requests_are_fired=True)
    def test_update_ntb(self):
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(
            os.path.join(dirname, "../fixtures", "ntb_event.xml")
        )

        with open(fixture, "rb") as f:
            body = f.read()

        responses.get("https://example.com/NTBEvent.xml", body=body, status=200)

        service = event_http_service.EventHTTPFeedingService()
        provider = {
            "feed_parser": "ntb_event_xml",
            "config": {
                "url": "https://example.com/NTBEvent.xml",
            },
            "is_closed": False,
            "_id": "ntb_event_xml",
            "name": "ntb_event_xml",
        }

        events = list(service.update(provider, {}))
        self.assertEqual(len(events), 1)

import os
import ntb
import responses

from responses import matchers
from superdesk.tests import TestCase
from ntb.io.feeding_services import ntb_event_api
from planning.events import init_app as init_events_app
from apps.prepopulate.app_populate import AppPopulateCommand


PROVIDER = {
    "_id": "test_ntb_events_api_xml",
    "feed_parser": "ntb_events_api_xml",
    "config": {
        "url": "https://nyheter.ntb.no/ntbWeb/api/x1/search/full?"
        "search.service=newscalendar&"
        "search.calendarStart=2018-10-01&"
        "search.calendarStop=2018-10-31",
        "username": "fake",
        "password": "fake",
    },
}


class NTBEventsApiFeedingServiceTestCase(TestCase):
    def setUp(self):
        super().setUp()

        with self.app.app_context():
            # prepopulate vocabularies
            voc_file = os.path.join(
                os.path.abspath(os.path.dirname(os.path.dirname(ntb.__file__))),
                "data",
                "vocabularies.json",
            )
            AppPopulateCommand().run(voc_file)
            # by default events resource is not available
            init_events_app(self.app)

        # NTBEventsApiFeedingService does 4 request during 1 update,
        self.feeds = []
        for i in range(4):
            dirname = os.path.dirname(os.path.realpath(__file__))
            fixture = os.path.normpath(
                os.path.join(
                    dirname, "../fixtures", "ntb_events_api", "{}.xml".format(i)
                )
            )

            with open(fixture, "rb") as f:
                self.feeds.append(f.read())

    @responses.activate(assert_all_requests_are_fired=True)
    def test_requests_offset(self):
        responses.get(
            "https://nyheter.ntb.no/ntbWeb/api/x1/search/full",
            match=(
                matchers.query_param_matcher({"search.offset": 0}, strict_match=False),
            ),
            body=self.feeds[0],
            status=200,
        )
        responses.get(
            "https://nyheter.ntb.no/ntbWeb/api/x1/search/full",
            match=(
                matchers.query_param_matcher({"search.offset": 2}, strict_match=False),
            ),
            body=self.feeds[1],
            status=200,
        )
        responses.get(
            "https://nyheter.ntb.no/ntbWeb/api/x1/search/full",
            match=(
                matchers.query_param_matcher({"search.offset": 4}, strict_match=False),
            ),
            body=self.feeds[2],
            status=200,
        )
        responses.get(
            "https://nyheter.ntb.no/ntbWeb/api/x1/search/full",
            match=(
                matchers.query_param_matcher({"search.offset": 6}, strict_match=False),
            ),
            body=self.feeds[3],
            status=200,
        )
        feeding_service = ntb_event_api.NTBEventsApiFeedingService()
        feeding_service.provider = PROVIDER
        items = feeding_service._update(PROVIDER, {})[0]
        assert 8 == len(items)

import os
from unittest import mock

from superdesk.tests import TestCase
from superdesk.vocabularies.commands import VocabulariesPopulateCommand
import ntb
from ntb.io.feeding_services import ntb_event_api
from planning.events import init_app as init_events_app


PROVIDER = {
    '_id': 'test_ntb_events_api_xml',
    'feed_parser': 'ntb_events_api_xml',
    'config': {
        'url': 'https://nyheter.ntb.no/ntbWeb/api/x1/search/full?'
               'search.service=newscalendar&'
               'search.calendarStart=2018-10-01&'
               'search.calendarStop=2018-10-31',
        'username': 'fake',
        'password': 'fake'
    },
}


class NTBEventsApiFeedingServiceTestCase(TestCase):

    def setUp(self):
        super().setUp()

        with self.app.app_context():
            # prepopulate vocabularies
            voc_file = os.path.join(
                os.path.abspath(os.path.dirname(os.path.dirname(ntb.__file__))), 'data', 'vocabularies.json'
            )
            VocabulariesPopulateCommand().run(voc_file)
            # by default events resource is not available
            init_events_app(self.app)

        # NTBEventsApiFeedingService does 4 request during 1 update,
        # to mock returning of different results (requests.get) self._side_effect is used
        self.feeds = []
        for i in range(4):
            dirname = os.path.dirname(os.path.realpath(__file__))
            fixture = os.path.normpath(
                os.path.join(dirname, '../fixtures', 'ntb_events_api_{}.xml'.format(i))
            )

            with open(fixture, 'rb') as f:
                self.feeds.append(f.read())

    def _side_effect(self, *args, **kwargs):
        m = mock.MagicMock()
        m.ok = True

        if kwargs['params']['search.offset'] == 0:
            m.content = self.feeds[0]
        elif kwargs['params']['search.offset'] == 2:
            m.content = self.feeds[1]
        elif kwargs['params']['search.offset'] == 4:
            m.content = self.feeds[2]
        elif kwargs['params']['search.offset'] == 6:
            m.content = self.feeds[3]

        return m

    @mock.patch.object(ntb_event_api.requests, 'get')
    def test_items_count(self, get):
        get.side_effect = self._side_effect
        feeding_service = ntb_event_api.NTBEventsApiFeedingService()
        items = feeding_service._update(PROVIDER, {})[0]

        self.assertEqual(len(items), 8)

    @mock.patch.object(ntb_event_api.requests, 'get')
    def test_items_count_ignore_duplicates(self, get):
        feeding_service = ntb_event_api.NTBEventsApiFeedingService()

        get.return_value.ok = True
        get.return_value.content = self.feeds[0]
        items = feeding_service._update(PROVIDER, {})[0]
        self.assertEqual(len(items), 2)

    @mock.patch.object(ntb_event_api.requests, 'get')
    def test_requests_offset(self, get):
        get.side_effect = self._side_effect
        feeding_service = ntb_event_api.NTBEventsApiFeedingService()
        feeding_service._update(PROVIDER, {})

        self.assertEqual(
            get.mock_calls[0],
            mock.call(
                PROVIDER['config']['url'],
                auth=('fake', 'fake'),
                params={'search.offset': 0, 'search.showNumResults': 25},
                timeout=20
            )
        )

        self.assertEqual(
            get.mock_calls[1],
            mock.call(
                PROVIDER['config']['url'],
                auth=('fake', 'fake'),
                params={'search.offset': 2, 'search.showNumResults': 25},
                timeout=20
            )
        )

        self.assertEqual(
            get.mock_calls[2],
            mock.call(
                PROVIDER['config']['url'],
                auth=('fake', 'fake'),
                params={'search.offset': 4, 'search.showNumResults': 25},
                timeout=20
            )
        )

        self.assertEqual(
            get.mock_calls[3],
            mock.call(
                PROVIDER['config']['url'],
                auth=('fake', 'fake'),
                params={'search.offset': 6, 'search.showNumResults': 25},
                timeout=20
            )
        )

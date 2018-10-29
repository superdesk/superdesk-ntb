import datetime

from ntb.io.feed_parsers.ntb_events_api_xml import NTBEventsApiXMLFeedParser
from . import XMLParserTestCase


class NTBEventsApiXMLTestCase(XMLParserTestCase):
    filename = 'ntb_events_api/0.xml'

    def setUp(self):
        self.parser = NTBEventsApiXMLFeedParser()
        super().setUp()
        # NTBEventsApiXMLFeedParser returns a list
        self.items = self.item

    def test_items(self):
        self.assertEqual(2, len(self.items))

    def test_ntb_id(self):
        self.assertIn('NBRP181003_093009_ga_00', self.items)
        self.assertIn('NBRP181001_152418_hh_00', self.items)

    def test_name(self):
        self.assertEqual(
            'ISHOCKEY: Eliteserien menn (18. runde):',
            self.items['NBRP181003_093009_ga_00']['name']
        )
        self.assertEqual(
            'LANGRENN: Lansering av boka om Oddvar Brå – Et skiløperliv.',
            self.items['NBRP181001_152418_hh_00']['name']
        )

    def test_dates(self):
        # DST, 2 hours difference
        self.assertEqual(
            datetime.datetime(2018, 9, 29, 16, 30, tzinfo=datetime.timezone.utc),
            self.items['NBRP181003_093009_ga_00']['dates']['start']
        )
        self.assertEqual(
            datetime.datetime(2018, 9, 29, 19, 30, tzinfo=datetime.timezone.utc),
            self.items['NBRP181003_093009_ga_00']['dates']['end']
        )
        # no DST
        self.assertEqual(
            datetime.datetime(2018, 11, 10, 11, 0, tzinfo=datetime.timezone.utc),
            self.items['NBRP181001_152418_hh_00']['dates']['start']
        )
        self.assertEqual(
            datetime.datetime(2018, 11, 10, 12, 0, tzinfo=datetime.timezone.utc),
            self.items['NBRP181001_152418_hh_00']['dates']['end']
        )

    def test_priority(self):
        self.assertEqual(5, self.items['NBRP181003_093009_ga_00']['priority'])
        self.assertEqual(5, self.items['NBRP181001_152418_hh_00']['priority'])

    def test_category(self):
        self.assertEqual('Utenriks', self.items['NBRP181003_093009_ga_00']['category'])
        self.assertEqual('Sport', self.items['NBRP181001_152418_hh_00']['category'])

    def test_calendars(self):
        self.assertNotIn('calendars', self.items['NBRP181003_093009_ga_00'])
        self.assertEqual([{'is_active': True, 'name': 'Sport', 'qcode': 'sport'}],
                         self.items['NBRP181001_152418_hh_00']['calendars'])

    def test_anpa_category(self):
        self.assertEqual(
            [{
                'is_active': True,
                'language': 'nb-NO',
                'name': 'Nyhetstjenesten',
                'qcode': 'n',
                'single_value': False
            }],
            self.items['NBRP181003_093009_ga_00']['anpa_category']
        )
        self.assertNotIn(
            'anpa_category',
            self.items['NBRP181001_152418_hh_00']
        )

    def test_location(self):
        self.assertEqual(
            [{'name': 'Tyskland', 'qcode': 'Tyskland'}],
            self.items['NBRP181003_093009_ga_00']['location']
        )
        self.assertNotIn('location', self.items['NBRP181001_152418_hh_00'])

    def test_subject(self):
        self.assertEqual(
            [{'scheme': 'subject_custom', 'name': 'Langrenn', 'qcode': '15043001'}],
            self.items['NBRP181001_152418_hh_00']['subject']
        )

    def test_slugline(self):
        slug = self.items['NBRP181003_093009_ga_00']['slugline'].split(' ')
        slug.sort()
        self.assertEqual(
            ['Ishockey', 'Nasjonal', 'toppliga'],
            slug
        )
        self.assertEqual(
            'Langrenn',
            self.items['NBRP181001_152418_hh_00']['slugline']
        )

    def test_occur_status(self):
        self.assertEqual(
            {'qcode': 'eocstat:eos5', 'name': 'Planned, occurs certainly', 'label': 'Planned, occurs certainly'},
            self.items['NBRP181003_093009_ga_00']['occur_status']
        )
        self.assertEqual(
            {'qcode': 'eocstat:eos5', 'name': 'Planned, occurs certainly', 'label': 'Planned, occurs certainly'},
            self.items['NBRP181001_152418_hh_00']['occur_status']
        )

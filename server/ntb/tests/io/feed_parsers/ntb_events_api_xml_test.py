import datetime

import superdesk
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
        self.assertIn('NBRP181003_093009_ga_00', self.items[0]['ntb_id'])
        self.assertIn('NBRP181001_152418_hh_00', self.items[1]['ntb_id'])

    def test_name(self):
        self.assertEqual(
            'ISHOCKEY: Eliteserien menn (18. runde):',
            self.items[0]['name']
        )
        self.assertEqual(
            'LANGRENN: Lansering av boka om Oddvar Brå – Et skiløperliv.',
            self.items[1]['name']
        )

    def test_dates(self):
        # DST, 2 hours difference
        self.assertEqual(
            datetime.datetime(2018, 9, 29, 16, 30, tzinfo=datetime.timezone.utc),
            self.items[0]['dates']['start']
        )
        self.assertEqual(
            datetime.datetime(2018, 9, 29, 19, 30, tzinfo=datetime.timezone.utc),
            self.items[0]['dates']['end']
        )
        # no DST
        self.assertEqual(
            datetime.datetime(2018, 11, 10, 11, 0, tzinfo=datetime.timezone.utc),
            self.items[1]['dates']['start']
        )
        self.assertEqual(
            datetime.datetime(2018, 11, 10, 12, 0, tzinfo=datetime.timezone.utc),
            self.items[1]['dates']['end']
        )

    def test_priority(self):
        self.assertEqual(5, self.items[0]['priority'])
        self.assertEqual(5, self.items[1]['priority'])

    def test_category(self):
        self.assertEqual('Utenriks', self.items[0]['category'])
        self.assertEqual('Sport', self.items[1]['category'])

    def test_calendars(self):
        self.assertNotIn('calendars', self.items[0])
        self.assertEqual([{'is_active': True, 'name': 'Sport', 'qcode': 'sport'}],
                         self.items[1]['calendars'])

    def test_anpa_category(self):
        self.assertEqual(
            [{
                'is_active': True,
                'language': 'nb-NO',
                'name': 'Nyhetstjenesten',
                'qcode': 'n',
                'selection_type': 'multi selection'
            }],
            self.items[0]['anpa_category']
        )
        self.assertNotIn(
            'anpa_category',
            self.items[1]
        )

    def test_location(self):
        self.assertEqual(
            [{'name': 'Tyskland', 'qcode': 'Tyskland'}],
            self.items[0]['location']
        )
        self.assertNotIn('location', self.items[1])

    def test_subject(self):
        self.assertEqual(
            [{'scheme': 'subject_custom', 'name': 'Langrenn', 'qcode': '15043001'}],
            self.items[1]['subject']
        )

    def test_slugline(self):
        slug = self.items[0]['slugline'].split(' ')
        slug.sort()
        self.assertEqual(
            ['Ishockey', 'Nasjonal', 'toppliga'],
            slug
        )
        self.assertEqual(
            'Langrenn',
            self.items[1]['slugline']
        )

    def test_occur_status(self):
        self.assertEqual(
            {'qcode': 'eocstat:eos5', 'name': 'Planned, occurs certainly', 'label': 'Planned, occurs certainly'},
            self.items[0]['occur_status']
        )
        self.assertEqual(
            {'qcode': 'eocstat:eos5', 'name': 'Planned, occurs certainly', 'label': 'Planned, occurs certainly'},
            self.items[1]['occur_status']
        )

    def test_definition_short(self):
        self.assertEqual(
            'Manglerud Star – Storhamar 18.30 (i Gjøvik fjellhall).\n            \n \n            \n \xa0\n            '
            '\n NÅR:   ma 29.10.2018 kl 18:30-21:30',
            self.items[0]['definition_short']
        )

        self.assertEqual(
            'Hunderfossen Familiepark er saksøkt av Caprino Filmcenter for attraksjonen, berg- og dalbanen Il Tempo '
            'Gigante. for krenkelse av opphavsrett. Hunderfossen fikk medhold i tingretten i 2015, Caprino Filmsenter '
            'vant i lagmannsretten i januar 2017, mens Høyesterett i oktober 2017 fastslo at feil lovanvendelse var '
            'brukt i lagmannsretten. Dermed møtes partene på nytt i Eidsivating lagmannsrett denne uka.\n            '
            '\n Saksnummer 17-187139ASD-ELAG/\n            \n Parter: Caprino Filmcenter AS og Hunderfossen Familiepark'
            ' AS, Kari og Kjell Aukrusts Stiftelse - Aukruststiftelsen.\n            \n Rettens administrator: Fritz '
            'Borgenholt.\n            \n Advokater: Tage Brigt Andreassen Skoghøy - Are Stenvik , Aslak Runde.\n      '
            '      \n \n            \n \xa0\n            \n NÅR:   ti 30.10.2018 - fr 02.11.2018  HVOR:   Eidsivating'
            ' lagmannsrett',
            self.items[1]['definition_short']
        )


class NTBEventsFTPApiXMLTestCase(XMLParserTestCase):
    filename = 'ntb_events_api/ftp_0.xml'

    def setUp(self):
        self.parser = NTBEventsApiXMLFeedParser()
        super().setUp()
        # NTBEventsApiXMLFeedParser returns a list
        self.item = self.item[0]

    def test_ntb_id(self):
        self.assertNotIn('ntb_id', self.item)

    def test_type(self):
        self.assertEqual('event', self.item['type'])

    def test_format(self):
        self.assertEqual('preserved', self.item['format'])

    def test_name(self):
        self.assertEqual('Klimatilpasningskonferansen 2018', self.item['name'])

    def test_dates(self):
        self.assertEqual('Europe/Oslo', self.item['dates']['tz'])
        self.assertEqual(
            self.item['dates']['start'],
            datetime.datetime(2018, 11, 29, 8, 45, tzinfo=datetime.timezone.utc)
        )
        self.assertEqual(
            self.item['dates']['end'],
            datetime.datetime(2018, 11, 29, 15, 0, tzinfo=datetime.timezone.utc)
        )

    def test_priority(self):
        self.assertEqual(5, self.item['priority'])

    def test_category(self):
        self.assertEqual('Innenriks', self.item['category'])

    def test_calendars(self):
        self.assertNotIn('calendars', self.item)

    def test_anpa_category(self):
        self.assertNotIn('anpa_category', self.item)

    def test_location(self):
        self.assertEqual(
            [{
                'name': 'Thon Hotel Arena, Lillestrøm',
                'qcode': 'Thon Hotel Arena, Lillestrøm'
            }],
            self.item['location']
        )

    def test_subject(self):
        self.assertNotIn('subject', self.item)

    def test_slugline(self):
        self.assertNotIn('slugline', self.item)

    def test_occur_status(self):
        self.assertEqual(
            {'qcode': 'eocstat:eos5', 'name': 'Planned, occurs certainly', 'label': 'Planned, occurs certainly'},
            self.item['occur_status']
        )

    def test_definition_short(self):
        self.assertEqual(
            'Hvordan tar kommunene i bruk kunnskap og praktiske verktøy for å tilpasse seg til klimaendringer, og '
            'hvordan kan sentrale myndigheter bidra? Samarbeid nasjonalt - styrke lokalt. Konferansen arrangeres av '
            'KS,DSB,Miljødirektoratet og NVE.',
            self.item['definition_short']
        )

    def test_links(self):
        self.assertEqual(
            ['https://egencia.qondor.com/klimatilpasningskonferansen'],
            self.item['links']
        )

    def test_internal_note(self):
        self.assertEqual(
            'Til NTB kalender. På forhånd takk.\nMarianne Fromreide, mfr@ks.no, 97643346',
            self.item['internal_note']
        )

    def test_event_contact_info_inculded(self):
        self.assertIn(
            'event_contact_info',
            self.item
        )
        self.assertEqual(1, len(self.item['event_contact_info']))

    def test_event_contact_info_fields(self):
        contacts = superdesk.get_resource_service(
            'contacts'
        ).get_from_mongo(req=None, lookup={})
        contacts = list(contacts)

        self.assertEqual(1, len(contacts))
        self.assertEqual(
            ['marit.finnland.troite@miljodir.no'],
            contacts[0]['contact_email']
        )
        self.assertEqual(
            [{'number': '99463198', 'usage': '', 'public': True, 'is_active': True}],
            contacts[0]['contact_phone']
        )
        self.assertEqual('Marit', contacts[0]['first_name'])
        self.assertEqual('Finnland Trøite', contacts[0]['last_name'])
        self.assertEqual(True, contacts[0]['is_active'])
        self.assertEqual(True, contacts[0]['public'])

    def test_event_contact_info_id(self):
        contacts = superdesk.get_resource_service(
            'contacts'
        ).get_from_mongo(req=None, lookup={})
        contacts = list(contacts)

        self.assertEqual(
            self.item['event_contact_info'][0],
            contacts[0]['_id']
        )

    def test_event_contact_info_not_duplicated(self):
        contacts = superdesk.get_resource_service(
            'contacts'
        ).get_from_mongo(req=None, lookup={})
        contacts = list(contacts)
        self.assertEqual(1, len(contacts))
        self._run_parse()
        contacts = superdesk.get_resource_service(
            'contacts'
        ).get_from_mongo(req=None, lookup={})
        contacts = list(contacts)
        self.assertEqual(1, len(contacts))

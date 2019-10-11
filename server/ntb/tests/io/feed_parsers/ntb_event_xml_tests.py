import xml.etree.ElementTree as ET
from ntb.io.feed_parsers.ntb_event_xml import NTBEventXMLFeedParser

from . import XMLParserTestCase


class NTBEventXMLFeedParserTestCase(XMLParserTestCase):
    filename = 'ntb_event.xml'
    parser = NTBEventXMLFeedParser()

    def test_ntb_event_xml_feed_parser_can_parse(self):
        self.assertTrue(NTBEventXMLFeedParser().can_parse(self.xml_root))
        self.assertFalse(NTBEventXMLFeedParser().can_parse(ET.fromstring("""
        <?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>
        <newsMessage></newsMessage>
        """.strip())))

    def test_ntb_event_xml_feed_parser_parse(self):
        self.assertEqual('MARKS XML TEST', self.item[0].get('name'))
        self.assertEqual('MARKS XML TEST.', self.item[0].get('definition_long'))
        self.assertEqual(
            {'end': '2016-09-16T16:00:00', 'tz': '', 'start': '2016-09-05T09:00:00'},
            self.item[0].get('dates'))

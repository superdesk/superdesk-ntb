# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013 - 2018 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from ntb.io.feed_parsers.dpa_newsml import DPANewsMLFeedParser
from . import XMLParserTestCase


class BaseDPANewsMLTestCase(XMLParserTestCase):
    def setUp(self):
        self.parser = DPANewsMLFeedParser()
        super().setUp()


class DPATestCase(BaseDPANewsMLTestCase):
    filename = 'dpa_newsml_test.xml'

    def test_can_parse(self):
        self.assertTrue(DPANewsMLFeedParser().can_parse(self.xml_root))

    def test_content(self):
        item = self.item[0]
        self.assertEqual(item['subject'], [{'qcode': 'Utenriks', 'name': 'Utenriks', 'scheme': 'category'}])
        self.assertEqual(item['anpa_category'], [{'name': 'Nyhetstjenesten', 'qcode': 'n'}])
        self.assertEqual(item['headline'], 'Chef von Ölkonzern Eni soll wegen Nigeria-Schmiergeldern vor Gericht')
        self.assertEqual(item['guid'], 'urn:newsml:dpa.com:20090101:171220-99-357156:6')
        self.assertEqual(item['uri'], 'urn:newsml:dpa.com:20090101:171220-99-357156')
        self.assertEqual(item['versioncreated'].isoformat(), '2017-12-20T14:49:36+01:00')
        self.assertEqual(item['firstcreated'].isoformat(), '2017-12-20T14:49:36+01:00')

        expected_body = ('<p>Rom (dpa) - Der Geschäftsführer des italienischen Energiekonzerns Eni, Claudio Descalzi, '
                         'muss wegen mutmaßlicher Schmiergeldzahlungen seiner Firma bei Auftragsvergaben in Nigeria vo'
                         'r Gericht. Ein Richter in Mailand ordnete am Mittwoch an, dass der Prozess gegen ihn und 14 '
                         'weitere Beschuldigte am 5. März beginnt, wie die italienische Nachrichtenagentur Ansa berich'
                         'tete. Mitangeklagt sind unter anderem Descalzis Vorgänger Paolo Scaroni sowie vier Manager d'
                         'es Rivalen Shell und Nigerias früherer Energieminister Dan Etete.</p><p>Die Vorwürfe gehen a'
                         'uf das Jahr 2011 zurück. Eni und Shell sollen damals an Etete Schmiergelder von etwa 1,1 Mil'
                         'lionen Dollar (etwa 931 000 Euro) gezahlt haben, um sich die Förderrechte für eines der größ'
                         'ten Ölfelder des westafrikanischen Landes - die Lizenz 246 - zu sichern. Zu der Zeit war Des'
                         'calzi Leiter von Enis Abteilung für Förderung und Produktion. Sowohl Eni als auch Shell weis'
                         'en die Vorwürfe zurück.  </p><p>Das Eni-Board vertraue weiter darauf, dass der Konzern nicht'
                         ' in die angeblichen Korruptionsvorwürfe verwickelt sei und drücke Descalzi sein volles Vertr'
                         'auen aus, hieß es in einer Mitteilung. Die Nachricht vom bevorstehenden Prozess stoppte den '
                         'Aufwärtstrend der Eni-Aktie  an der Mailänder Börse. Zuvor hatten den Titel Nachrichten befl'
                         'ügelt, der Konzern habe mit der Gasgewinnung im Offshore-Feld Zohr vor Ägyptens Küste begonn'
                         'en. Es wird vermutet, dass dieses Gasfeld das größte im Mittelmeer ist. </p>')

        self.assertEqual(item['body_html'], expected_body)
        self.assertEqual(item['urgency'], 5)

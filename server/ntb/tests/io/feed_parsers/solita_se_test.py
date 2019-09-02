# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013 - 2018 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from ntb.io.feed_parsers.solita_se import SolitaSE
from . import XMLParserTestCase


class BaseSolitaTestCase(XMLParserTestCase):
    def setUp(self):
        self.parser = SolitaSE()
        super().setUp()


class STTTestCase(BaseSolitaTestCase):
    filename = 'solita_se_1.xml'

    def test_can_parse(self):
        """Check that can_parse return True on solita file"""
        self.assertTrue(SolitaSE().can_parse(self.xml_root))

    def test_content(self):
        """Check majors metadata"""
        item = self.item[0]
        self.assertEqual(item['type'], 'text')
        self.assertEqual(item['guid'], 'solita-se_ntb:announcement:8-no')
        self.assertEqual(item['headline'], 'Dette er tittelen')
        self.assertEqual(item['slugline'], 'Cypress Test publisher')
        self.assertEqual(item['anpa_category'], [{"name": "Formidlingstjenester", "qcode": "r"}])
        self.assertEqual(item['genre'], [{"name": "Fulltekstmeldinger", "qcode": "Fulltekstmeldinger",
                                          "scheme": "genre_custom"}])

        self.assertIn({'qcode': 'Børsmelding', 'name': 'Børsmelding', 'scheme': 'category'}, item['subject'])
        self.assertEqual(
            item['body_html'],
            '<!-- title --><!-- byline --><p>2.4.2019 16:02:09 CEST | Cypress Test publisher | Årsrapport</p><!-- leadt'
            'ext -->\nDette er ingressen\n<!-- body -->\n<p>Dette er brødteksten. Dette er brødteksten. Dette er brødte'
            'ksten. Dette er brødteksten. Dette er brødteksten. Dette er brødteksten. Dette er brødteksten. Dette er br'
            'ødteksten. Dette er brødteksten. Dette er brødteksten. Dette er brødteksten.\xa0</p>\n<p>Dette er brødteks'
            'ten. Dette er brødteksten. Dette er brødteksten. Dette er brødteksten. Dette er brødteksten. Dette er brød'
            'teksten. Dette er brødteksten. Dette er brødteksten. Dette er brødteksten. Dette er brødteksten. Dette er '
            'brødteksten. Dette er brødteksten. Dette er brødteksten. Dette er brødteksten. Dette er brødteksten.\xa0</'
            'p>\n<p>Dette er brødteksten. Dette er brødteksten. Dette er brødteksten. Dette er brødteksten. Dette er br'
            'ødteksten. Dette er brødteksten. Dette er brødteksten. Dette er brødteksten. Dette er brødteksten. Dette e'
            'r brødteksten.\xa0</p>\n<!-- legal disclaimer -->\n<h4>Ansvarsfraskrivelse</h4>\n<p>Dette er den norske an'
            'svarsfraskrivelsesteksten</p>\n<!-- contacts -->\n<h4>Kontakter</h4>\n<ul><li>\n        Lennart Lie-Havste'
            'in\n        Produktsjef\n        +47 942 77 795\n        <a href="mailto:lennart.lie-havstein@ntb.no">lenn'
            'art.lie-havstein@ntb.no</a>\n    </li></ul>\n<!-- boilerplate -->\n<h4>Om Cypress Test publisher</h4>\n<p>'
            'Dette er den norske Om oss- teksten</p>\n<!-- attachments -->\n<h4>Vedlegg</h4>\n<ul><li><a href="https://'
            'prs-ntb-beta.solitaservices.fi/ir-files/42/8/2/2019-02-22%20-%20Hjemstatsliste.pdf">2019-02-22 - Hjemstats'
            'liste.pdf</a></li></ul>\n\n        '
        )

        self.assertEqual(item['ednote'], '*** Dette er en børsmelding formidlet av NTB pva. andre ***')
        self.assertEqual(item['extra']['ntb_pub_name'], 'Cypress Test publisher')


class STTTestCase2(BaseSolitaTestCase):
    filename = 'solita_se_2.xml'

    def test_can_parse(self):
        """Check that can_parse return True on solita file"""
        self.assertTrue(SolitaSE().can_parse(self.xml_root))

    def test_content(self):
        """Check that original announcement and category are added to body (cf. SDNTB-592)"""
        item = self.item[0]
        self.assertEqual(
            item['body_html'],
            '<p>Mandatory notification of trade primary insiders</p><p class="prs-announcement__byline">15.7.2019 12:09'
            ':11 CEST | TESTKUNDE BØRS ASA | Meldepliktig handel for primærinnsidere</p><p>Dette er en ingress</p><p>De'
            'tte er en brødtekst.</p><p/><table class="prs-table"><tr class="prs-table__row--light"><td>Dette er en tab'
            'ell</td><td>2017</td><td>2018</td><td>2019</td></tr><tr><td>Inntekter</td><td>3</td><td>4</td><td>5</td></'
            'tr><tr><td>Kostnader</td><td>2</td><td>3</td><td>4</td></tr><tr><td>Resultat</td><td>1</td><td>2</td><td>3'
            '</td></tr></table><p/><h4>Informasjonspliktig opplysning</h4><p>Denne opplysningen er informasjonspliktig '
            'etter verdipapirhandelloven § 5-12</p><h4>Kontakter</h4><ul><li>\n        Lennart Lie-Havstein\n        Pr'
            'oduktsjef\n        +47 942 77 795\n        <a href="mailto:llh@ntb.no">llh@ntb.no</a>\n    </li></ul><h4>O'
            'm TESTKUNDE BØRS ASA</h4><p>Dette er en om oss-tekst i en børsmelding</p><h4>Vedlegg</h4><ul><li><a href="'
            'https://prs-ntb-beta.solitaservices.fi/ir-files/17847073/6/5/Hjemstatsliste%20Oslo%20Bors.pdf">Hjemstatsli'
            'ste Oslo Bors.pdf</a></li><li><a href="https://prs-ntb-beta.solitaservices.fi/ir-files/17847073/6/6/Medlem'
            'sliste%20Oslo%20Bors.pdf">Medlemsliste Oslo Bors.pdf</a></li></ul><p>Se saken i sin helhet: <a href="https'
            '://prs-ntb-beta.solitaservices.fi/announcement?announcementId=6&amp;lang=no">https://prs-ntb-beta.solitase'
            'rvices.fi/announcement?announcementId=6&amp;lang=no</a></p>'
        )

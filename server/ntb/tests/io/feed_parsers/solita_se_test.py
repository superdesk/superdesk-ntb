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
        self.assertEqual(item['slugline'], 'Borsmelding-nordicir.com')
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

# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013 - 2018 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from ntb.io.feed_parsers.ritzau import RitzauFeedParser
from . import XMLParserTestCase


class BaseRitzauTestCase(XMLParserTestCase):
    def setUp(self):
        self.parser = RitzauFeedParser()
        super().setUp()


class RitzauTestCase(BaseRitzauTestCase):
    filename = 'ritzau.xml'

    def test_can_parse(self):
        self.assertTrue(RitzauFeedParser().can_parse(self.xml_root))

    def test_content(self):
        item = self.item
        subject_expected = [{'qcode': 'Utenriks', 'name': 'Utenriks', 'scheme': 'category'}]
        self.assertEqual(item['subject'], subject_expected)
        self.assertEqual(item['anpa_category'], [{'name': 'Nyhetstjenesten', 'qcode': 'n'}])
        self.assertEqual(item['version'], 1)
        self.assertEqual(item['byline'], '/ritzau/')
        self.assertEqual(item['guid'], '9a6955fc-11da-46b6-9903-439ebb288f2d')
        self.assertEqual(item['firstcreated'].isoformat(), '2018-01-30T17:32:18.397000+01:00')
        expected_body = ('<p>Hollandske forskere har "i årevis" lavet forsøg på både mennesker og dyr, hvor de har tes'
                         'tet effekten af at indånde udstødningsgas fra dieselbiler.</p><p>Det fortæller forskerne sel'
                         'v til nyhedsbureauet AFP.</p><p>Historien kommer frem på et tidspunkt, hvor tyske bilfabrika'
                         'nter er udsat for massiv kritik, fordi de har finansieret lignende forsøg.</p>')
        self.assertEqual(item['body_html'], expected_body)


class RitzauTestCase2(BaseRitzauTestCase):
    filename = 'ritzau_2.xml'

    def test_can_parse(self):
        self.assertTrue(RitzauFeedParser().can_parse(self.xml_root))

    def test_content(self):
        item = self.item
        subject_expected = [
            {'name': 'Politikk',
             'qcode': '11000000',
             'scheme': 'subject_custom'},
            {'name': 'Forsvar',
             'qcode': '11001000',
             'scheme': 'subject_custom'},
            {'name': 'Vitenskap og teknologi',
             'qcode': '13000000',
             'scheme': 'subject_custom'},
            {'name': 'Sosiale forhold',
             'qcode': '14000000',
             'scheme': 'subject_custom'},
            {'name': 'Utenriks', 'qcode': 'Utenriks', 'scheme': 'category'}]
        self.assertEqual(sorted(item['subject'], key=lambda i: i['qcode']), subject_expected)
        self.assertEqual(item['anpa_category'], [{'name': 'Nyhetstjenesten', 'qcode': 'n'}])
        self.assertEqual(item['version'], 1)
        self.assertEqual(item['byline'], '/ritzau/')
        self.assertEqual(item['headline'], 'Forsvaret sender satellit ud i rummet for første gang')
        self.assertEqual(item['abstract'], 'En ny, danskudviklet satellit skal udføre overvågningsopgaver i '
                                           'Arktis for det danske Forsvar.<br />')
        self.assertEqual(item['guid'], 'b5342fc2-b3e1-4331-ab2b-5e93e0d59427')
        self.assertEqual(item['firstcreated'].isoformat(), '2018-01-31T18:45:36.730000+01:00')
        expected_body = ('<p>En danskudviklet minisatellit – en såkaldt cubesat - bliver sendt ud i rummet fredag, hvi'
                         's alt går efter planen. Det skriver Videnskab.dk.</p><p>Satellitten er ejet og betalt af For'
                         'svarsministeriet, og den skal udføre overvågningsopgaver for Forsvaret i Arktis.</p> <p>- De'
                         't er første gang, at Forsvaret sender sin egen satellit ud i rummet.</p><p>- Hvis det bliver'
                         ' en succes, kan det blive et skridt imod, at Forsvaret engagerer sig mere i at bruge rummet,'
                         ' siger Charlotte Wiin Havsteen, ansvarlig for projektet ved Forsvarsministeriets Materiel- o'
                         'g Indkøbsstyrelse, til Videnskab.dk.</p> <p>Satellitten er udviklet i et samarbejde mellem D'
                         'anmarks Tekniske Universitet (DTU) og rumvirksomheden GomSpace i Aalborg.</p> <p>Den måler b'
                         'lot 30x20x10 centimeter og indeholder radiomodtagere, der kan opfange positionssignaler fra '
                         'skibe og fly.</p><p>Herudover sidder der også et kamera på satellitten, som kan tage billede'
                         'r af Arktis, når vejret er klart.</p> <p>- Den vejer kun otte kilo, og den er så lille, at d'
                         'en kan være i en almindelig Fjällräven-rygsæk, fortæller Charlotte Wiin Havsteen.</p> <p>- S'
                         'atellitten skal hjælpe med at løse forsvarets opgave med overvågningen i Arktis. Den kan giv'
                         'e et overblik over, hvem der er i området, og hvad de laver.</p> <p>Forsvaret har betalt 11,'
                         '7 millioner kroner for satellitten. Prisen dækker både det videnskabelige udviklingsarbejde '
                         'og opsendelse af satellitten.</p> <p>- Det er et helt nyt spring for forsvaret at gå ind i r'
                         'umalderen. Tidligere har de selvfølgelig brugt udenlandske satellitdata ligesom alle os andr'
                         'e, men det er første gang, at de får deres egen satellit.</p><p>- Det er selvfølgelig rigtig'
                         ' interessant for os, der er i rumbranchen, siger astrofysiker og direktør for DTU Space Kris'
                         'tian Pedersen til Videnskab.dk.</p><p>Satellitten bærer navnet Ulloriaq, som betyder "stjern'
                         'e" på grønlandsk. Den vil blive sendt afsted fra Kina fredag om bord på en kinesisk "Long Ma'
                         'rch"-løfteraket, hvis vejret tillader det.</p><p>Hvis Ulloriaqs bidrag til overvågningen af '
                         'Arktis er en succes, kan den måske blive den første i en række af nanosatellitter, som kan b'
                         'live sendt ud i rummet af det danske forsvar, skriver Videnskab.dk.</p><p>I forbindelse med '
                         'opsendelsen af Forsvarets nye satellit vil en anden danskbygget satellit også blive sendt ud'
                         ' i rummet.</p> <p>Denne satellit, som kaldes GomX-4B, er ligeledes bygget af den nordjyske v'
                         'irksomhed GomSpace. Den er finansieret af den europæiske rumfartsorganisation ESA og har hel'
                         't andre opgaver end forsvarets Ulloriaq-satellit.</p><p>/ritzau/</p>')
        self.assertEqual(item['body_html'], expected_body)

# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013 - 2018 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from ntb.io.feed_parsers.tt_newsml import TTNewsMLFeedParser
from . import XMLParserTestCase


class BaseTTNewsMLTestCase(XMLParserTestCase):
    def setUp(self):
        self.parser = TTNewsMLFeedParser()
        super().setUp()


class TTTestCase(BaseTTNewsMLTestCase):
    filename = 'tt_newsml_test.xml'

    def test_can_parse(self):
        self.assertTrue(TTNewsMLFeedParser().can_parse(self.xml_root))

    def test_content(self):
        item = self.item[0]
        self.assertEqual(item['subject'], [{'qcode': 'Utenriks', 'name': 'Utenriks', 'scheme': 'category'}])
        self.assertEqual(item['anpa_category'], [{'name': 'Nyhetstjenesten', 'qcode': 'n'}])
        self.assertEqual(item['headline'], 'Polen: EU hämnas för flyktingmotstånd')
        self.assertEqual(item['guid'], 'urn:newsml:tt.se:20171220:TT:585167:0')
        self.assertEqual(item['uri'], 'urn:newsml:tt.se:20171220:TT:585167:0')
        self.assertEqual(item['firstcreated'].isoformat(), '2017-12-20T14:46:21+01:00')
        self.assertEqual(item['abstract'], 'För första gången sedan EU:s Lissabonfördrag trädde i kraft tar EU-kommiss'
                                           'ionen i med sin storslägga mot ett medlemsland. Polen riskerar nu formellt'
                                           ' indragen rösträtt - även om vägen dit fortfarande är lång.\n            '
                                           '\nI Warszawa tror man att åtgärden är en hämnd för landets ovilja att ta e'
                                           'mot flyktingar.\n          ')

        expected_body = ('<h1>Polen: EU hämnas för flyktingmotstånd</h1>\n          \n<p>EU / Bryssel, TT:s korrespond'
                         'ent</p>\n            \n<p>För första gången sedan EU:s Lissabonfördrag trädde i kraft tar EU'
                         '-kommissionen i med sin storslägga mot ett medlemsland. Polen riskerar nu formellt indragen '
                         'rösträtt - även om vägen dit fortfarande är lång.</p>\n            \n<p>I Warszawa tror man '
                         'att åtgärden är en hämnd för landets ovilja att ta emot flyktingar.</p>\n          \n       '
                         '   \n            \n<blockquote>Tyvärr har vår oro fördjupats, konstaterar EU-kommissionens f'
                         'örste viceordförande Frans Timmermans om Polen efter dagens kommissionsmöte i Bryssel.</bloc'
                         'kquote>\n            \n<blockquote>Vi har gett tre rekommendationer och hela tiden varit red'
                         'o för en dialog. Men någon dialog har aldrig ägt rum, säger Timmermans.</blockquote>\n      '
                         '      \n<p>Som väntat konstaterar därmed kommissionen att det finns risk för att Polen bryte'
                         'r mot EU:s grundläggande rättigheter, vilket i slutändan kan leda till att landet blir av me'
                         'd sin rösträtt i EU-sammanhang.</p>\n            \n<h2>"Politiskt beslut"</h2>\n            '
                         '\n<p>Från polsk sida avfärdas dock även dagens agerande i Bryssel.</p>\n            \n<block'
                         'quote>Det här beslutet har inget värde. Det är enligt vår mening bara ett rent politiskt bes'
                         'lut, säger Beata Mazurek, taleskvinna för regeringspartiet PIS, enligt nyhetsbyrån PAP.</blo'
                         'ckquote>\n            \n<p>Mazurek tror att EU-kommissionens agerande kan vara ett sätt att '
                         'hämnas på Polen för landets ovilja att ta emot flyktingar.</p>\n            \n<blockquote>De'
                         't här kan vara en följd inte bara av oppositionens uppgifter (om Polen till EU), utan också '
                         'av att vi inte vill ta emot invandrare, vi vill inte ta emot muslimska migranter, eftersom v'
                         'i bryr oss om säkerheten för polackerna.</blockquote>\n            \n<p>Tvisten gäller ändri'
                         'ngar i tillsättningar, pensionsålder och befogenheter inom det polska rättsväsendet som Pole'
                         'ns regering genomfört under de senaste åren. Eftersom Polen inte ansett sig behöva reagera p'
                         'å kommissionens oro kommer sanktionsbollen nu att skickas vidare till EU:s medlemsländer.</p'
                         '>\n            \n<h2>"Jättesorgligt"</h2>\n            \n<p>Den svenska ledamoten i EU-kommi'
                         'ssionen, Cecilia Malmström, konstaterar att kommissionen försökt och försökt, men inte komme'
                         'r längre.</p>\n            \n<blockquote>Två år av förhandlingar, samtal, meddelanden, utstr'
                         'äckta händer, hot och löften har inte lett till något resultat i Polen, säger Malmström till'
                         ' TT.</blockquote>\n            \n<blockquote>Det är jättesorgligt att Polen, som är ett land'
                         ' som vi alla har vänner i och som vi beundrar och som spelar en enorm roll i den europeiska '
                         'unionen, har en regering som tyvärr bryter så flagrant mot de grundläggande värderingarna i '
                         'EU att det bara blir sämre. Det här är tyvärr den enda utvägen, säger Malmström.</blockquote'
                         '>\n            \n<h2>Jämförs med Sovjet</h2>\n            \n<p>EU-kommissionen hänvisar blan'
                         'd annat till kritik från Europarådets Venedigkommission.</p>\n            \n<blockquote>De j'
                         'ämför ju det polska systemet med det gamla Sovjetsystemet, med totalt statligt inflytande öv'
                         'er rättsväsendet. Och det är mycket allvarligt. Det strider mot Polens egen författning och '
                         'mot alla värderingar i den Europeiska unionen. Polen hade inte fått bli medlem i dag, säger '
                         'Malmström.</blockquote>\n            \n<p>EU-minister Ann Linde kallar åtgärden "en mycket a'
                         'llvarlig påtryckning". Hon ser det som troligt att en majoritet av länderna fastställer att '
                         'Polen riskerar att bryta mot unionens grundläggande värderingar. Att enhälligt slå fast att '
                         'de faktiskt gör det ser Linde som "betydligt svårare".</p>\n            \n<h2>Upptrappad dis'
                         'kussion</h2>\n            \n<p>Samtidigt har diskussionen trappats upp om att kunna villkora'
                         ' Polens EU-bidrag om de inte följer rättsstatens principer, säger Linde.</p>\n            \n'
                         '<blockquote>Förhoppningen är att när man nu kommer med så entydiga rekommendationer från fle'
                         'ra olika håll, att Polen då ska lyssna på detta och förstå att det är seriöst. Dessutom är d'
                         'et så att alla länder, även Sverige, vill ha en bra relation med Polen.</blockquote>\n      '
                         '      \n<p>Närmast blir det nu upp till EU:s medlemsländer att avgöra om det finns en "klar '
                         'risk" för att Polen "åsidosätter" grundläggande värderingar. Det beslutet behöver i så fall '
                         'tas med fyra femtedelars majoritet - minst 22 medlemsländer.</p>\n            \n<blockquote>'
                         'Nu måste detta upp på högsta nivå bland medlemsländerna och så hoppas vi att de kan ha en al'
                         'lvarlig diskussion om detta och att de kan påverka Polen, säger Malmström.</blockquote>\n   '
                         '         \n<h2>Stöd från Ungern?</h2>\n            \n<p>För att verkligen införa sanktioner '
                         'mot Polen krävs sedan i nästföljande läge total enighet bland de övriga EU-länderna. Det ans'
                         'es dock osannolikt, bland annat med tanke på tidigare uttalat stöd till Polen från exempelvi'
                         's Ungern.</p>\n            \n<p>Cecilia Malmström hoppas dock att själva processen leder til'
                         'l att eventuella stödländer verkligen tänker till på förhand.</p>\n            \n<blockquote'
                         '>Då måste också de länderna som motarbetar detta säga varför de försvarar att Polen har infö'
                         'rt ett sådant här rättssystem. Då måste de medlemsländerna komma fram och säga varför de int'
                         'e tycker att det här kräver någon form av åtgärder, säger Cecilia Malmström till TT.</blockq'
                         'uote>\n          \n          \n<p><a>Wiktor Nummelin/TT</a></p>\n        \n        \n       '
                         '   \n<h1>Fakta: EU:s storslägga</h1>\n          \n            \n<p>I artikel 7 i EU:s Lissab'
                         'onfördrag fastställs att en majoritet i EU-kommissionen, EU-parlamentet eller bland medlemsl'
                         'änderna kan dra igång ett särskilt förfarande när det finns "en klar risk för att en medlems'
                         'stat allvarligt åsidosätter värdena i artikel 2".</p>\n            \n<p>Det som nämns i arti'
                         'kel 2 är bland annat "respekt för människans värdighet, frihet, demokrati, jämlikhet, rättss'
                         'taten och respekt för de mänskliga rättigheterna, inklusive rättigheter för personer som til'
                         'lhör minoriteter".</p>\n            \n<p>I artikel 7 stipuleras fyra steg:</p>\n            '
                         '\n<ul>\n              <li>1) fastställande att det finns "en klar risk" för att ett land åsi'
                         'dosätter värdena. Behöver göras av minst fyra femtedelar av övriga EU-länder.</li>\n        '
                         '      <li>2) fastställande att ett land verkligen åsidosätter värdena. Ska göras enhälligt a'
                         'v samtliga övriga EU-länder utom det utpekade landet.</li>\n              <li>3) beslut att '
                         'tillfälligt upphäva exempelvis landets rösträtt. Måste också göras enhälligt.</li>\n        '
                         '      <li>4) beslut att ändra eller återkalla tidigare åtgärder.</li>\n            </ul>\n  '
                         '          \n<p>Källa: Lissabonfördraget.</p>\n            \n<p></p>\n            \n<p></p>\n'
                         '          \n        \n      ')

        self.assertEqual(item['body_html'], expected_body)

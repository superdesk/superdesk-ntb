# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.tests import TestCase
from unittest import mock
from ntb.publish.ntb_nitf import NTBNITFFormatter
from ntb.publish.ntb_nitf import ENCODING
from superdesk.publish.formatters import Formatter
from superdesk.publish.subscribers import SubscribersService
from superdesk.publish import init_app
from lxml import etree
import datetime
import uuid
import pytz
import copy

TEST_ABSTRACT = "This is the abstract"
TEST_NOT_LEAD = "This should not be lead"
TEST_EMAILS = ('test1@test.tld', 'test2@example.net', 'test3@example.org')
ITEM_ID = str(uuid.uuid4())
NOW = datetime.datetime.now(datetime.timezone.utc)
TEST_BODY = """
<p class="lead" lede="true">""" + TEST_NOT_LEAD + """</p>
<p class="txt">line 1</p>
<p>line 2</p>
<p class="toto">line 3</p>
<p class="txt-ind" style="style_should_be:'removed'">test encoding: –</p>
<!-- EMBED START Image {id: "embedded18237840351"} --><figure>
<img src="http://scanpix.no/spWebApp/previewimage/sdl/preview/tb42bf43.jpg" alt="alt text" />
<figcaption>New parliament speaker Ana Pastor speaks on her phone during the first session of parliament\
following a general election in Madrid, Spain, July 19, 2016. REUTERS/Andrea Comas</figcaption>
</figure><!-- EMBED END Image {id: "embedded18237840351"} -->
<h3>intermediate line</h3>
<p>this element should have a txt class</p>
<!-- EMBED START Video {id: "embedded10005446043"} --><figure>
<video controls="controls">
</video>
<figcaption>SCRIPT TO FOLLOW</figcaption>
</figure><!-- EMBED END Video {id: "embedded10005446043"} -->
"""
ARTICLE = {
    'headline': 'test headline',
    'abstract': TEST_ABSTRACT,
    'body_html': TEST_BODY,
    'type': 'text',
    'priority': '2',
    '_id': 'urn:localhost.abc',
    'item_id': ITEM_ID,
    'family_id': ITEM_ID,
    # we use non latin1 chars in slugline to test encoding
    "slugline": "this is the slugline œ:?–",
    'urgency': 2,
    'versioncreated': NOW,
    '_current_version': 5,
    'version': 5,
    'rewrite_sequence': 1,
    'language': 'nb-NO',
    'body_footer': 'footer text',
    'sign_off': '/'.join(TEST_EMAILS),
    # if you change place, please keep a test with 'parent': None
    # cf SDNTB-290
    'place': [{'scheme': 'place_custom', 'parent': None, 'name': 'Global', 'qcode': 'Global'}],
    'dateline': {
        'located': {
            'dateline': 'city',
            'tz': 'Europe/Oslo',
            'city': 'Hammerfest',
            'state': 'Finnmark',
            'alt_name': '',
            'country': 'Norway',
            'state_code': 'NO.20',
            'country_code': 'NO',
            'city_code': 'Hammerfest'},
        'source': 'NTB',
        'text': 'HAMMERFEST, Sep 13  -'},
    'subject': [
        {"scheme": "category",
         "qcode": "Forskning",
         "service": {
             "f": 1,
             "i": 1},
         "name": "Forskning"},
        {"scheme": "subject_custom",
         "qcode": "02001003",
         "parent": "02000000",
         "name": "tyveri og innbrudd"}],
    "associations": {

        "featuremedia": {
            "_id": "test_id",
            "guid": "test_id",
            "headline": "feature headline",
            "ingest_provider": "fdsfdsfsdfs",
            "original_source": "feature_source",
            "pubstatus": "usable",
            "renditions": {
                "baseImage": {
                    "href": "http://scanpix.no/spWebApp/previewimage/sdl/preview_big/test_id.jpg"
                },
                "thumbnail": {
                    "href": "http://preview.scanpix.no/thumbs/tb/4/33/test_id.jpg"
                },
                "viewImage": {
                    "href": "http://scanpix.no/spWebApp/previewimage/sdl/preview/test_id.jpg"
                }},
            "source": "feature_source",
            "fetch_endpoint": "scanpix",
            "type": "picture",
            "versioncreated": NOW,
            "description_text": "test feature media"
        },

        "embedded01": None,
        "embedded10005446043": {
            "firstcreated": "2016-07-19T16:23:11+0000",
            "original_source": "Reuters DV",
            "_updated": "1970-01-01T00:00:00+0000",
                        "mimetype": "video/mpeg",
                        "renditions": {
                            "viewImage": {
                                "href": "http://scanpix.no/spWebApp/previewimage/sdl/preview/tb42bf38.jpg"
                            },
                            "baseImage": {
                                "href": "http://scanpix.no/spWebApp/previewimage/sdl/preview/tb42bf38.jpg"
                            },
                            "thumbnail": {
                                "href": "http://preview.scanpix.no/thumbs/tb/4/2b/tb42bf38.jpg"
                            }
                        },
            "_etag": "85294f12036b2bb9f97cb9e421961dd330cd1d3d",
            "pubstatus": "usable",
            "source": "Reuters DV",
            "versioncreated": NOW,
            "_created": "1970-01-01T00:00:00+0000",
            "byline": None,
            "fetch_endpoint": "scanpix",
            "type": "video",
            "guid": "tb42bf38",
            "_id": "tb42bf38",
            "description_text": "\n\nSCRIPT TO FOLLOW\n",
            "_type": "externalsource",
            "ingest_provider": "577148e1cc3a2d5ab90f5d9c",
            "_links": {
                "self": {
                    "href": "scanpix(desk)/tb42bf38",
                    "title": "Scanpix(desk)"}},
            "headline": "Hollande meets Portugal president"
        },
        "embedded18237840351": {
            "firstcreated": "2016-07-19T16:23:17+0000",
            "original_source": "Reuters",
            "_updated": "1970-01-01T00:00:00+0000",
                        "renditions": {
                            "viewImage": {
                                "href": "http://scanpix.no/spWebApp/previewimage/sdl/preview/tb42bf43.jpg"
                            },
                            "baseImage": {
                                "href": "http://scanpix.no/spWebApp/previewimage/sdl/preview_big/tb42bf43.jpg"
                            },
                            "thumbnail": {
                                "href": "http://preview.scanpix.no/thumbs/tb/4/2b/tb42bf43.jpg"
                            }
                        },
            "pubstatus": "usable",
            "_etag": "238529c614736dc314165bca1f0da523b82a2d2a",
            "source": "Reuters",
            "versioncreated": NOW,
            "_created": "1970-01-01T00:00:00+0000",
            "byline": "Andrea Comas",
            "fetch_endpoint": "scanpix",
            "type": "picture",
            "guid": "tb42bf43",
            "_id": "tb42bf43",
            "description_text": "New parliament speaker Ana Pastor speaks on her"
            " phone during the first "
            "session of parliament following a general election in Madrid, Spain,"
            " July 19, 2016. REUTERS/Andrea Comas",
            "_type": "externalsource",
            "ingest_provider": "577148e1cc3a2d5ab90f5d9c",
            "_links": {
                "self": {
                    "href": "scanpix(desk)/tb42bf43",
                    "title": "Scanpix(desk)"}},
            "headline": "New parliament speaker Ana Pastor speaks on her phone during the first session o"
                        "f parliament following a general election in Madrid"
        },
        "embedded03": None,
    },
}


class NTBNITFFormatterTest(TestCase):

    def __init__(self, *args, **kwargs):
        super(NTBNITFFormatterTest, self).__init__(*args, **kwargs)
        self.article = None

    @mock.patch.object(SubscribersService, 'generate_sequence_number', lambda self, subscriber: 1)
    def setUp(self):
        super().setUp()
        self.formatter = NTBNITFFormatter()
        self.base_formatter = Formatter()
        init_app(self.app)
        self.tz = pytz.timezone(self.app.config['DEFAULT_TIMEZONE'])
        if self.article is None:
            # formatting is done once for all tests to save time
            # as long as used attributes are not modified, it's fine
            self.article = ARTICLE
            self.formatter_output = self.formatter.format(self.article, {'name': 'Test NTBNITF'})
            self.doc = self.formatter_output[0]['encoded_item']
            self.nitf_xml = etree.fromstring(self.doc)

    def test_subject_and_category(self):
        tobject = self.nitf_xml.find('head/tobject')
        self.assertEqual(tobject.get('tobject.type'), 'Forskning')
        subject = tobject.find('tobject.subject')
        self.assertEqual(subject.get('tobject.subject.refnum'), '02001003')
        self.assertEqual(subject.get('tobject.subject.matter'), 'tyveri og innbrudd')

    def test_slugline(self):
        du_key = self.nitf_xml.find('head/docdata/du-key')
        self.assertEqual(du_key.get('key'), 'this is the slugline œ:?–')

    def test_doc_id(self):
        doc_id = self.nitf_xml.find('head/docdata/doc-id')
        self.assertEqual(doc_id.get('regsrc'), 'NTB')
        self.assertEqual(doc_id.get('id-string'), 'NTB{}_{:02}'.format(ITEM_ID, 1))

    def test_pubdata(self):
        pubdata = self.nitf_xml.find('head/pubdata')
        expected = NOW.astimezone(self.tz).strftime("%Y%m%dT%H%M%S")
        self.assertEqual(pubdata.get('date.publication'), expected)
        self.assertEqual(pubdata.get('item-length'), '121')
        self.assertEqual(pubdata.get('unit-of-measure'), "character")

    def test_dateline(self):
        dateline = self.nitf_xml.find('body/body.head/dateline')
        self.assertEqual(dateline.text, 'Hammerfest')

    def test_body(self):
        # body content
        body_content = self.nitf_xml.find("body/body.content")
        p_elems = iter(body_content.findall('p'))
        lead = next(p_elems)
        self.assertEqual(lead.get("class"), "lead")
        self.assertEqual(lead.text, TEST_ABSTRACT)
        not_lead = next(p_elems)
        self.assertEqual(not_lead.get("class"), "txt-ind")
        self.assertEqual(not_lead.text, TEST_NOT_LEAD)

        p_lead = body_content.findall('p[@class="lead"]')
        self.assertEqual(len(p_lead), 1)

        for i in range(1, 4):
            p = next(p_elems)
            self.assertEqual(p.text, "line {}".format(i))
            self.assertEqual(p.get("class"), "txt-ind")

        p_encoding = next(p_elems)
        self.assertEqual(p_encoding.text, "test encoding: –")
        self.assertNotIn("style", p_encoding.attrib)

        hl2 = body_content.find('hl2')
        self.assertEqual(hl2.text, "intermediate line")

        p_cls_txt = next(p_elems)
        # <p> elements following <hl2> must have a "txt" class
        self.assertEqual(p_cls_txt.get("class"), "txt")

        # all embedded must be removed from body's HTML,
        # they are put in <media/> elements
        self.assertNotIn(b'EMBED', etree.tostring(body_content))

        # medias

        medias = body_content.findall("media")
        feature = medias[0]
        self.assertEqual(feature.get("media-type"), "image")
        self.assertEqual(feature.find("media-reference").get("source"), "test_id")
        self.assertEqual(feature.find("media-caption").text, "test feature media")

        image = medias[1]
        self.assertEqual(image.get("media-type"), "image")
        self.assertEqual(image.find("media-reference").get("source"), "tb42bf43")
        self.assertEqual(image.find("media-caption").text,
                         "New parliament speaker Ana Pastor speaks on her phone during the first session of parliament"
                         " following a general election in Madrid, Spain, July 19, 2016. REUTERS/Andrea Comas")
        video = medias[2]
        self.assertEqual(video.get("media-type"), "video")
        self.assertEqual(video.find("media-reference").get("mime-type"), "video/mpeg")
        self.assertEqual(video.find("media-reference").get("source"), "tb42bf38")
        self.assertEqual(video.find("media-caption").text, "\n\nSCRIPT TO FOLLOW\n")

    def test_sign_off(self):
        a_elems = self.nitf_xml.findall("body/body.end/tagline/a")
        assert len(a_elems) == len(TEST_EMAILS)
        emails = list(TEST_EMAILS)
        for a_elem in a_elems:
            email = emails.pop(0)
            self.assertEqual(a_elem.get('href'), 'mailto:{}'.format(email))
            self.assertEqual(a_elem.text, email)
            if emails:  # only the last element has not "/" in tail
                self.assertEqual(a_elem.tail, '/')

    @mock.patch.object(SubscribersService, 'generate_sequence_number', lambda self, subscriber: 1)
    def test_empty_dateline(self):
        """SDNTB-293 regression test"""
        article = copy.deepcopy(self.article)
        article['dateline'] = {'located': None}
        formatter_output = self.formatter.format(article, {'name': 'Test NTBNITF'})
        doc = formatter_output[0]['encoded_item']
        nitf_xml = etree.fromstring(doc)
        self.assertEqual(nitf_xml.find('body/body.head/dateline'), None)

    @mock.patch.object(SubscribersService, 'generate_sequence_number', lambda self, subscriber: 1)
    def test_prefix_cleaning(self):
        """SDNTB-313 regression test"""
        article = copy.deepcopy(self.article)
        article['abstract'] = ''
        del article['associations']
        article['body_html'] = "<pref:h1><other_pref:body.content><t:t/>toto</other_pref:body.content></pref:h1>"
        expected = (b'<body.content><p class="lead" lede="true" />toto<p class="txt">'
                    b'footer text</p></body.content>')
        formatter_output = self.formatter.format(article, {'name': 'Test NTBNITF'})
        doc = formatter_output[0]['encoded_item']
        nitf_xml = etree.fromstring(doc)
        body_content = nitf_xml.find("body/body.content")
        self.assertEqual(b''.join(etree.tostring(body_content).split()), b''.join(expected.split()))

    @mock.patch.object(SubscribersService, 'generate_sequence_number', lambda self, subscriber: 1)
    def test_single_counter(self):
        """SDNTB-338 regression test"""
        # media counter should appear once and only once when no image is present
        article = copy.deepcopy(self.article)
        article['body_html'] = "<p/>"
        del article['associations']
        formatter_output = self.formatter.format(article, {'name': 'Test NTBNITF'})
        doc = formatter_output[0]['encoded_item']
        nitf_xml = etree.fromstring(doc)
        head = nitf_xml.find('head')
        media_counters = head.findall('meta[@name="NTBBilderAntall"]')
        self.assertEqual(len(media_counters), 1)
        self.assertEqual(media_counters[0].get('content'), '0')

    @mock.patch.object(SubscribersService, 'generate_sequence_number', lambda self, subscriber: 1)
    def test_351(self):
        """SDNTB-351 regression test

        unbound namespaces must be removed from attributes
        """
        article = copy.deepcopy(self.article)
        article['abstract'] = ""
        article['body_html'] = """\
            <p class="BrdtekstInnrykk">Målet i kortbane-VM som nylig ble avsluttet
            i den canadiske byen Windsor var personlig rekord på <st1:metricconverter productid="1500 meter"
            w:st="on">1500 meter</st1:metricconverter><br></p>
            """
        expected = b"""\
            <body.content><p class="lead" lede="true" /><p class="txt-ind">M&#229;let i
            kortbane-VM som nylig ble avsluttet i den canadiske byen Windsor var personlig rekord p&#229; 1500
            meter</p><p class="txt">footer text</p><media media-type="image"><media-reference mime-type="image/jpeg"
            source="test_id" /><media-caption>test feature media</media-caption></media></body.content>
            """.replace(b'\n', b'').replace(b' ', b'')
        formatter_output = self.formatter.format(article, {'name': 'Test NTBNITF'})
        doc = formatter_output[0]['encoded_item']
        nitf_xml = etree.fromstring(doc)
        body_content = nitf_xml.find("body/body.content")
        self.assertEqual(etree.tostring(body_content).replace(b'\n', b'').replace(b' ', b''), expected)

    @mock.patch.object(SubscribersService, 'generate_sequence_number', lambda self, subscriber: 1)
    def test_355(self):
        """SDNTB-355 regression test

        formatter should not crash when featuremedia is None
        """
        article = copy.deepcopy(self.article)
        article['associations']['featuremedia'] = None
        formatter_output = self.formatter.format(article, {'name': 'Test NTBNITF'})
        doc = formatter_output[0]['encoded_item']
        nitf_xml = etree.fromstring(doc)
        # the test will raise an exception during self.formatter.format if SDNTB-355 bug is still present
        # but we check in addition that media counter is as expected
        media_counter = nitf_xml.find('head').find('meta[@name="NTBBilderAntall"]')
        self.assertEqual(media_counter.get('content'), '2')

    @mock.patch.object(SubscribersService, 'generate_sequence_number', lambda self, subscriber: 1)
    def test_358(self):
        """SDNTB-358 regression test

        invalid characters should be stripped
        """
        article = copy.deepcopy(self.article)
        bad_char_txt = "SKJÆ\x12R I SJØEN: Kirken Gospa od Skrpjela"
        article['associations']['embedded10005446043']["description_text"] = bad_char_txt
        article['body_html'] += bad_char_txt
        # formatting in next line will fail with body_html if invalid chars are not stripped
        formatter_output = self.formatter.format(article, {'name': 'Test NTBNITF'})
        doc = formatter_output[0]['encoded_item']
        # next line will fail if SDNTB-358 is still present
        etree.fromstring(doc)

    @mock.patch.object(SubscribersService, 'generate_sequence_number', lambda self, subscriber: 1)
    def test_388(self):
        """SDNTB-388 regression test

        check that &nbsp; between 2 words is not resulting in the 2 words being merged
        """
        article = copy.deepcopy(self.article)
        article['abstract'] = ''
        del article['associations']
        del article['body_footer']
        article['body_html'] = "<p>word1&nbsp;word2</p>"
        formatter_output = self.formatter.format(article, {'name': 'Test NTBNITF'})
        doc = formatter_output[0]['encoded_item']
        nitf_xml = etree.fromstring(doc)
        p_content = nitf_xml.find("body/body.content/p[@class='txt-ind']").text
        # there must be a space between the two words
        self.assertEqual(p_content, "word1 word2")

    @mock.patch.object(SubscribersService, 'generate_sequence_number', lambda self, subscriber: 1)
    def test_390(self):
        """SDNTB-390 regression test

        formatter should not crash when an embedded is None
        """
        article = copy.deepcopy(self.article)
        article['associations']['embedded18237840351'] = None
        formatter_output = self.formatter.format(article, {'name': 'Test NTBNITF'})
        doc = formatter_output[0]['encoded_item']
        nitf_xml = etree.fromstring(doc)
        media_counter = nitf_xml.find('head').find('meta[@name="NTBBilderAntall"]')
        # the test will raise an exception during self.formatter.format if SDNTB-390 bug is still present
        # but we check in addition that media counter is as expected (same as for test_355)
        self.assertEqual(media_counter.get('content'), '2')

    @mock.patch.object(SubscribersService, 'generate_sequence_number', lambda self, subscriber: 1)
    def test_pretty_formatting(self):
        """check that content is pretty formatted

        we use here a body_html with spaces added on purpose, and check that resulting
        body.content is formatted as expected
        """
        article = copy.deepcopy(self.article)
        article['abstract'] = ""
        article['body_html'] = """\
            <div><div class="outer"> <h1>test title</h1>
        <p>test <strong>strong</strong>  </p> <div><p>

        <ul> <li> item 1</li>     <li>item 2</li>   <li>item 3</li>  </p>

        </div></div>  </div>
        <p>foo<br></p>
        <p>bar</p>
            """
        article['associations'] = {}
        formatter_output = self.formatter.format(article, {'name': 'Test NTBNITF'})
        doc = formatter_output[0]['encoded_item']
        body_content = doc[doc.find(b'<body.content>') - 4:doc.find(b'</body.content>') + 15]
        expected = b"""\
    <body.content>
      <p class="lead" lede="true"></p>
      <hl2>test title</hl2>
      <p class="txt">test <em class="bold">strong</em>  </p>
      <p class="txt-ind">
        <ul>
          <li> item 1</li>
          <li>item 2</li>
          <li>item 3</li>
        </ul>
      </p>
      <p class="txt-ind">foo</p>
      <p class="txt-ind">bar</p>
      <p class="txt">footer text</p>
    </body.content>"""
        self.assertEqual(body_content, expected, body_content.decode('utf-8'))

    def test_filename(self):
        filename = self.nitf_xml.find('head/meta[@name="filename"]')
        datetime = NOW.astimezone(self.tz).strftime("%Y-%m-%d_%H-%M-%S")
        self.assertEqual(filename.get('content'), datetime + "__Forskning_ny1-this-is-the-slugline-----.xml")

    def test_encoding(self):
        encoded = self.formatter_output[0]['encoded_item']
        formatted = self.formatter_output[0]['formatted_item']
        manually_encoded = formatted.encode(ENCODING, 'xmlcharrefreplace')
        self.assertEqual(b''.join(encoded.split()), b''.join(manually_encoded.split()))
        header = formatted[:formatted.find('>') + 1]
        self.assertIn('encoding="{}"'.format(ENCODING), header)

    def test_place(self):
        evloc = self.nitf_xml.find('head/docdata/evloc')
        self.assertEqual(evloc.get('county-dist'), "Global")

    def test_meta(self):
        head = self.nitf_xml.find('head')

        media_counter = head.find('meta[@name="NTBBilderAntall"]')
        self.assertEqual(media_counter.get('content'), '3')
        editor = head.find('meta[@name="NTBEditor"]')
        self.assertEqual(editor.get('content'), 'Superdesk')
        kode = head.find('meta[@name="NTBDistribusjonsKode"]')
        self.assertEqual(kode.get('content'), 'ALL')
        kanal = head.find('meta[@name="NTBKanal"]')
        self.assertEqual(kanal.get('content'), 'A')
        ntb_id = head.find('meta[@name="NTBID"]')
        self.assertEqual(ntb_id.get('content'), 'NTB' + ITEM_ID)

    @mock.patch.object(SubscribersService, 'generate_sequence_number', lambda self, subscriber: 1)
    def test_update_id(self):
        """Check use of family_id on update

        when family id is different from item_id (i.e. on updated item),
        family_id should be used for doc-id and ntbid
        """
        article = copy.deepcopy(self.article)
        family_id = "test_family_id"
        article['family_id'] = family_id
        article['rewrite_sequence'] = 3
        formatter_output = self.formatter.format(article, {'name': 'Test NTBNITF'})
        doc = formatter_output[0]['encoded_item']
        nitf_xml = etree.fromstring(doc)
        head = nitf_xml.find('head')
        ntb_id = head.find('meta[@name="NTBID"]')
        self.assertEqual(ntb_id.get('content'), 'NTB' + family_id)
        doc_id = nitf_xml.find('head/docdata/doc-id')
        self.assertEqual(doc_id.get('regsrc'), 'NTB')
        self.assertEqual(doc_id.get('id-string'), 'NTB{}_{:02}'.format(family_id, 3))

    @mock.patch.object(SubscribersService, 'generate_sequence_number', lambda self, subscriber: 1)
    def test_description_text_none(self):
        """Check that parsing is not failing when description_text of an association exists and is None

        SDNTB-396 regression test
        """
        article = copy.deepcopy(self.article)
        article['associations']['featuremedia']['description_text'] = None
        formatter_output = self.formatter.format(article, {'name': 'Test NTBNITF'})
        doc = formatter_output[0]['encoded_item']
        nitf_xml = etree.fromstring(doc)
        # the test will raise an exception during self.formatter.format if SDNTB-396 bug is still present
        # but we check in addition that media counter is as expected (same as for test_355)
        media_counter = nitf_xml.find('head').find('meta[@name="NTBBilderAntall"]')
        self.assertEqual(media_counter.get('content'), '3')

    @mock.patch.object(SubscribersService, 'generate_sequence_number', lambda self, subscriber: 1)
    def test_body_none(self):
        article = copy.deepcopy(self.article)
        article['body_html'] = None
        formatter_output = self.formatter.format(article, {'name': 'Test NTBNITF'})
        # the test will raise an exception during self.formatter.format if SDNTB-420 bug is still present
        # but we also check that body.content is there
        doc = formatter_output[0]['encoded_item']
        nitf_xml = etree.fromstring(doc)
        expected = ('<body.content><pclass="lead"lede="true">Thisistheabstract</p><pclass="txt">footertext</p><mediame'
                    'dia-type="image"><media-referencemime-type="image/jpeg"source="test_id"/><media-caption>testfeatu'
                    'remedia</media-caption></media></body.content>')
        content = etree.tostring(nitf_xml.find('body/body.content'),
                                 encoding="unicode").replace('\n', '').replace(' ', '')
        self.assertEqual(content, expected)

    @mock.patch.object(SubscribersService, 'generate_sequence_number', lambda self, subscriber: 1)
    def test_rewrite_sequence_none(self):
        article = copy.deepcopy(self.article)
        article['rewrite_sequence'] = None
        formatter_output = self.formatter.format(article, {'name': 'Test NTBNITF'})
        doc = formatter_output[0]['encoded_item']
        nitf_xml = etree.fromstring(doc)
        doc_id = nitf_xml.find('head/docdata/doc-id')
        self.assertEqual(doc_id.get('id-string'), 'NTB{}_{:02}'.format(article['family_id'], 0))

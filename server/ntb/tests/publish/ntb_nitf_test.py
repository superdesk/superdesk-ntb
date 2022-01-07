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
from flask import json
import superdesk
import pathlib
import datetime
import uuid
import pytz
import copy

TEST_ABSTRACT = "This is the abstract"
TEST_NOT_LEAD = "This should not be lead"
TEST_EMAILS = ('test1@test.tld', 'test2@example.net', 'test3@example.org')
ITEM_ID = str(uuid.uuid4())
NTB_MEDIA_TXT = 'NTBMEDIA TO REMOVE'
NOW = datetime.datetime.now(datetime.timezone.utc)
TEST_BODY = """
<p lede="true" class="lead">""" + TEST_NOT_LEAD + """</p>
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
<p class="ntb-media"><a url="http://example.net/something.jpg">test</a>""" + NTB_MEDIA_TXT + """</p>
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
    'profile': '5ba11fec0d6f1301ac3cbd13',
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
    'place': [
        {
            'scheme': 'place_custom',
            'parent': None,
            'ntb_parent': None,
            'name': 'Global',
            'qcode': 'Global',
            'ntb_qcode': 'Global',
        }
    ],
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
        {
            'scheme': 'category',
            'qcode': 'Forskning',
            'service': {'f': 1, 'i': 1},
            'name': 'Forskning',
        },
        {
            'scheme': 'subject_custom',
            'qcode': '02001003',
            'parent': '02000000',
            'name': 'tyveri og innbrudd',
        },
    ],
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
    "extra": {
        "ntb_pub_name": "test ntb_pub_name",
        "ntb_media": [
            {
                "id": "1234",
                "url": "https://www.example.net/ntb_media_test.jpg",
                "mime_type": "image/jpeg",
                "description_text": "this is a test ntb media"
            }
        ]
    },
}


ARTICLE_WITH_IMATRICS_FIELDS = {
    "_id": "5ba1224e0d6f13056bd82d50",
    "family_id": "5ba1224e0d6f13056bd82d50",
    "type": "text",
    "version": 1,
    "profile": "5ba11fec0d6f1301ac3cbd14",
    "format": "HTML",
    "template": "5ba11fec0d6f1301ac3cbd15",
    "headline": "custom media field multi",
    "slugline": "test custom media2",
    "guid": "123",
    "subject": [
        {
            "name": "olje- og gassindustri",
            "qcode": "20000550",
            "source": "imatrics",
            "altids": {
                "imatrics": "1171f64b-1580-3a9e-add6-27fd59e435d2",
                "medtop": "20000550",
            },
            "scheme": "topics",
        },
        {
            "altids": {"imatrics": "66417b95-3ad5-35c3-8b5a-6dec0d4e0946"},
            "imatrics": "66417b95-3ad5-35c3-8b5a-6dec0d4e0946",
            "name": "Olje",
            "qcode": "66417b95-3ad5-35c3-8b5a-6dec0d4e0946",
            "scheme": "imatrics_topic",
            "source": "imatrics",
        },
        {
            "altids": {
                "medtop": "20001253",
                "imatrics": "1a8abfa6-b64a-3fe8-82eb-7144e62516ec",
            },
            "parent": "20000568",
            "scheme": "topics",
            "name": "matlaging",
            "qcode": "20001253",
            "source": "imatrics",
            "original_source": None,
        },
    ],
    "organisation": [
        {
            "altids": {
                "imatrics": "2d824ae1-ab9b-3227-870e-0810be0ebed0",
                "wikidata": "Q1",
            },
            "imatrics": "2d824ae1-ab9b-3227-870e-0810be0ebed0",
            "name": "Stortinget",
            "qcode": "2d824ae1-ab9b-3227-870e-0810be0ebed0",
            "source": "imatrics",
            "original_source": "wikidata",
        }
    ],
    "person": [
        {
            "altids": {
                "imatrics": "211de295-4da5-34b6-9960-cf5b86957e5d",
                "wikidata": "Q2",
            },
            "imatrics": "211de295-4da5-34b6-9960-cf5b86957e5d",
            "name": "Ola Borten Moe",
            "qcode": "211de295-4da5-34b6-9960-cf5b86957e5d",
            "source": "imatrics",
            "original_source": "wikidata",
        }
    ],
    "place": [
        {
            "name": "Oslo",
            "qcode": "6ea6e497-53dd-3086-928d-158b8c48a22a",
            "parent": "1edf0e8a-1a64-32a1-9122-74d9f088e46c",
            "source": "imatrics",
            "aliases": [
                "Kristiania",
                "Christiania"
            ],
            "original_source": "1013",
            "altids": {
                "imatrics": "6ea6e497-53dd-3086-928d-158b8c48a22a",
                "wikidata": "Q585"
            },
            "description": "hovedstad i Norge"
        },
    ],
    "versioncreated": NOW,
    "rewrite_sequence": 1,
    "language": "nb-NO",
    "body_footer": "footer text",
}


with open(pathlib.Path(__file__).parent.parent.parent.parent / "data" / "vocabularies.json") as f:
    vocabularies = json.load(f)


class NTBNITFFormatterTest(TestCase):

    def __init__(self, *args, **kwargs):
        super(NTBNITFFormatterTest, self).__init__(*args, **kwargs)
        self.article = None
        self.article_with_imatrics_fields = None

    @mock.patch.object(SubscribersService, 'generate_sequence_number', lambda self, subscriber: 1)
    def setUp(self):
        super().setUp()
        self.formatter = NTBNITFFormatter()
        self.base_formatter = Formatter()
        init_app(self.app)
        self.tz = pytz.timezone(self.app.config['DEFAULT_TIMEZONE'])
        self.app.data.insert("vocabularies", vocabularies)
        if self.article is None:
            # formatting is done once for all tests to save time
            # as long as used attributes are not modified, it's fine
            self.article = ARTICLE
            self.article_with_imatrics_fields = ARTICLE_WITH_IMATRICS_FIELDS
            self.formatter_output = self.formatter.format(self.article, {'name': 'Test NTBNITF'})
            self.doc = self.formatter_output[0]['encoded_item']
            self.nitf_xml = etree.fromstring(self.doc)
            self.formatter_output_imatrics = self.formatter.format(
                self.article_with_imatrics_fields, {"name": "Test NTBNITF"}
            )
            self.doc_imatrics = self.formatter_output_imatrics[0]["encoded_item"]
            self.nitf_xml_imatrics = etree.fromstring(self.doc_imatrics)

    def test_subject_and_category(self):
        tobject = self.nitf_xml.find("head/tobject")
        self.assertEqual(tobject.get("tobject.type"), "Forskning")
        subject = tobject.findall("tobject.subject")
        self.assertEqual(2, len(subject))
        self.assertEqual(subject[0].get("tobject.subject.refnum"), "02001003")
        self.assertEqual(subject[0].get("tobject.subject.matter"), "tyveri og innbrudd")
        self.assertEqual(subject[1].get("tobject.subject.refnum"), "02000000")
        self.assertEqual(subject[1].get("tobject.subject.type"), "Kriminalitet og rettsvesen")

    def test_subject_and_category_with_imatrics(self):
        tobject = self.nitf_xml_imatrics.find("head/tobject")
        subject = tobject.findall("tobject.subject")
        self.assertEqual(2, len(subject))
        self.assertEqual(subject[0].get("tobject.subject.refnum"), "10014000")
        self.assertEqual(subject[0].get("tobject.subject.matter"), "Bil")
        self.assertEqual(subject[1].get("tobject.subject.refnum"), "10000000")
        self.assertEqual(subject[1].get("tobject.subject.type"), "Fritid")

    def test_slugline(self):
        du_key = self.nitf_xml.find('head/docdata/du-key')
        self.assertEqual(du_key.get('key'), 'this is the slugline ----')

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
        # we must not have ntb-media <p> element
        # we can't use the "ntb-media" class, because all classes are changed to
        # "txt" or "txt-ind", so we use NTB_MEDIA_TXT to check if element is here
        p_ntb_media_elem = body_content.xpath('p[text()="{}"]'.format(NTB_MEDIA_TXT))
        self.assertEqual(p_ntb_media_elem, [])
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

        ntb_media = medias[3]
        self.assertEqual(ntb_media.get("media-type"), "image")
        self.assertEqual(ntb_media.get("class"), "prs")
        self.assertEqual(ntb_media.find("media-reference").get("source"), "https://www.example.net/ntb_media_test.jpg")
        self.assertEqual(ntb_media.find("media-reference").get("alternate-text"), "http://www.ntbinfo.no/")
        self.assertEqual(ntb_media.find("media-caption").text, "this is a test ntb media")

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
        expected = (
            '<body.content><p lede="true" class="lead"/>toto<p class="txt">footer text</p><media media-type="image" cla'
            'ss="prs"><media-reference mime-type="image/jpeg" alternate-text="http://www.ntbinfo.no/" source="https://w'
            'ww.example.net/ntb_media_test.jpg"/><media-caption>this is a test ntb media</media-caption></media></body.'
            'content>'
        )
        formatter_output = self.formatter.format(article, {'name': 'Test NTBNITF'})
        doc = formatter_output[0]['encoded_item']
        nitf_xml = etree.fromstring(doc)
        body_content = ' '.join(etree.tostring(nitf_xml.find("body/body.content"), encoding="unicode").split())
        self.assertEqual(body_content, expected)

    @mock.patch.object(SubscribersService, 'generate_sequence_number', lambda self, subscriber: 1)
    def test_single_counter(self):
        """SDNTB-338 regression test"""
        # media counter should appear once and only once when no image is present
        article = copy.deepcopy(self.article)
        article['body_html'] = "<p/>"
        del article['associations']
        del article['extra']
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
        expected = (
            '<body.content> <p lede="true" class="lead"/> <p class="txt-ind">Målet i kortbane-VM som nylig ble avslutte'
            't i den canadiske byen Windsor var personlig rekord på 1500 meter</p> <p class="txt">footer text</p> <medi'
            'a media-type="image" class="illustrasjonsbilde"> <media-reference mime-type="image/jpeg" source="test_id"/'
            '> <media-caption>test feature media</media-caption> </media> <media media-type="image" class="prs"> <media'
            '-reference mime-type="image/jpeg" alternate-text="http://www.ntbinfo.no/" source="https://www.example.net/'
            'ntb_media_test.jpg"/> <media-caption>this is a test ntb media</media-caption> </media> </body.content>'
        )
        formatter_output = self.formatter.format(article, {'name': 'Test NTBNITF'})
        doc = formatter_output[0]['encoded_item']
        nitf_xml = etree.fromstring(doc)
        body_content = ' '.join(etree.tostring(nitf_xml.find("body/body.content"), encoding='unicode').split())
        self.assertEqual(body_content, expected)

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
        self.assertEqual(media_counter.get('content'), '3')

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
        self.assertEqual(media_counter.get('content'), '3')

    @mock.patch.object(SubscribersService, 'generate_sequence_number', lambda self, subscriber: 1)
    def test_pretty_formatting(self):
        """Check that content is pretty formatted
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
        expected = (b"""\
    <body.content>
      <p lede="true" class="lead"></p>
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
      <media media-type="image" class="prs">
        <media-reference mime-type="image/jpeg" alternate-text="http://www.ntbinfo.no/" source"""
                    b"""="https://www.example.net/ntb_media_test.jpg"/>
        <media-caption>this is a test ntb media</media-caption>
      </media>
    </body.content>""")
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
        self.assertEqual(media_counter.get('content'), '4')
        editor = head.find('meta[@name="NTBEditor"]')
        self.assertEqual(editor.get('content'), 'Superdesk')
        kode = head.find('meta[@name="NTBDistribusjonsKode"]')
        self.assertEqual(kode.get('content'), 'ALL')
        kanal = head.find('meta[@name="NTBKanal"]')
        self.assertEqual(kanal.get('content'), 'A')
        ntb_id = head.find('meta[@name="NTBID"]')
        self.assertEqual(ntb_id.get('content'), 'NTB' + ITEM_ID)
        ntb_kilde = head.find('meta[@name="NTBKilde"]')
        self.assertEqual(ntb_kilde.get('content'), 'test ntb_pub_name')
        # priority
        ntb_kilde = head.find('meta[@name="NTBNewsValue"]')
        self.assertEqual(ntb_kilde.get('content'), '2')

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
        self.assertEqual(media_counter.get('content'), '4')

    @mock.patch.object(SubscribersService, 'generate_sequence_number', lambda self, subscriber: 1)
    def test_body_none(self):
        article = copy.deepcopy(self.article)
        article['body_html'] = None
        formatter_output = self.formatter.format(article, {'name': 'Test NTBNITF'})
        # the test will raise an exception during self.formatter.format if SDNTB-420 bug is still present
        # but we also check that body.content is there
        doc = formatter_output[0]['encoded_item']
        nitf_xml = etree.fromstring(doc)
        expected = (
            '<body.content> <p lede="true" class="lead">This is the abstract</p> <p class="txt">footer text</p> <media '
            'media-type="image" class="illustrasjonsbilde"> <media-reference mime-type="image/jpeg" source="test_id"/> '
            '<media-caption>test feature media</media-caption> </media> <media media-type="image" class="prs"> <media-r'
            'eference mime-type="image/jpeg" alternate-text="http://www.ntbinfo.no/" source="https://www.example.net/nt'
            'b_media_test.jpg"/> <media-caption>this is a test ntb media</media-caption> </media> </body.content>'
        )
        content = ' '.join(etree.tostring(nitf_xml.find('body/body.content'),
                                          encoding="unicode").split())
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

    @mock.patch.object(SubscribersService, 'generate_sequence_number', lambda self, subscriber: 1)
    def test_language_empty(self):
        article = copy.deepcopy(self.article)
        article.pop('language')
        self.formatter.format(article, {'name': 'Test NTBNITF'})

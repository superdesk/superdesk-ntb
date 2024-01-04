import pathlib

from flask import json
from unittest import mock
from ntb.publish.ntb_ninjs import NTBNINJSFormatter
from superdesk.tests import TestCase
from datetime import datetime
from .ntb_nitf_test import TEST_BODY


FAMILY_ID = "abcd"

TEST_BODY_EXPECTED = """
<p>This should not be lead</p>
<p>line 1</p>
<p>line 2</p>
<p>line 3</p>
<p>test encoding: –</p>

<h3>intermediate line</h3>
<p>this element should have a txt class</p>
<p><a>test</a>NTBMEDIA TO REMOVE</p>

<p>(©MyCompany2023)</p>
<p>footer this is</p>
""".strip()

with open(
    pathlib.Path(__file__).parent.joinpath("fixtures", "text-item-with-table.json")
) as f:
    text_item_with_table = json.load(f)


@mock.patch(
    "superdesk.publish.subscribers.SubscribersService.generate_sequence_number",
    lambda self, subscriber: 1,
)
class Ninjs2FormatterTest(TestCase):
    maxDiff = None
    article = {
        "_id": "5ba1224e0d6f13056bd82d50",
        "family_id": FAMILY_ID,
        "assignment_id": "assignment-id",
        "rewrite_sequence": 3,
        "type": "text",
        "version": 1,
        "profile": "5ba11fec0d6f1301ac3cbd14",
        "format": "HTML",
        "template": "5ba11fec0d6f1301ac3cbd15",
        "headline": "custom media field multi",
        "slugline": "test custom media2",
        "byline": "byline",
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
            {
                "name": "Fritid",
                "qcode": "10000000",
                "parent": None,
                "scheme": "subject_custom",
            },
        ],
        "organisation": [
            {
                "name": "Events DC",
                "description": "Events DC is a semi-public company in Washington, D",
                "qcode": "4e42b5e7-bfbe-3c2b-9188-d263e8a147e2",
                "source": "imatrics",
                "altids": {
                    "imatrics": "4e42b5e7-bfbe-3c2b-9188-d263e8a147e2",
                    "wikidata": "Q16837590",
                },
                "aliases": [],
                "original_source": "wikidata",
            }
        ],
        "person": [
            {
                "name": "Hanjigeer",
                "description": "Ming dynasty person CBDB = 124590",
                "qcode": "f1d109e7-a5ae-3f7c-8a1d-5bce4a70bf64",
                "source": "imatrics",
                "altids": {
                    "imatrics": "f1d109e7-a5ae-3f7c-8a1d-5bce4a70bf64",
                    "wikidata": "Q45489119",
                },
                "aliases": ["he ji ji er", "he"],
                "original_source": "wikidata",
            }
        ],
        "place": [
            {
                "altids": {
                    "wikidata": "Q57084",
                    "imatrics": "b564b1e1-1a99-324e-b643-88e5398305c6",
                },
                "aliases": ["Gjerdrum kommune"],
                "scheme": "place_custom",
                "name": "Gjerdrum",
                "description": "kommune i Viken",
                "qcode": "b564b1e1-1a99-324e-b643-88e5398305c6",
                "source": "imatrics",
                "original_source": "1013",
            },
            {
                "scheme": "place_custom",
                "name": "Global",
                "qcode": "Global",
            },
            {
                "aliases": [],
                "altids": {
                    "imatrics": "34017822-d341-3826-ab94-71d226d639c4",
                },
                "name": "Genève",
                "original_source": None,
                "qcode": "34017822-d341-3826-ab94-71d226d639c4",
                "scheme": "place_custom",
                "source": "imatrics",
            },
        ],
        "object": [
            {
                "name": "Tata LPT 613",
                "description": "kjøretøymodell",
                "qcode": "9227b7fa-92c0-3593-a3b7-96a84deedf75",
                "source": "imatrics",
                "altids": {
                    "imatrics": "9227b7fa-92c0-3593-a3b7-96a84deedf75",
                    "wikidata": "Q12072602",
                },
                "aliases": [],
                "original_source": "wikidata",
            }
        ],
        "event": [
            {
                "name": "Noise Eve",
                "description": "An event for testing",
                "qcode": "23333-4ff44ff-fkkf4-kfkk444",
                "source": "imatrics",
                "altids": {
                    "imatrics": "23333-4ff44ff-fkkf4-kfkk444",
                    "wikidata": "Q72065689",
                },
                "aliases": [],
                "original_source": "wikidata",
            }
        ],
        "versioncreated": "2022-08-09T13:38:58+0000",
        "language": "nb-NO",
        "priority": 6,
        "urgency": 3,
        "sign_off": "admin@example.com/foo@bar.com",
        "language": "nb-NO",
        "operation": "publish",
        "version_creator": "ObjectId(" "5640a5eef40235008465242b" ")",
        "abstract": "<p>abstract this is</p>",
        "body_html": TEST_BODY,
        "body_footer": "<p>footer this is</p>",
        "dateline": {
            "located": {
                "dateline": "city",
                "tz": "Europe/Oslo",
                "city": "Hammerfest",
                "state": "Finnmark",
                "alt_name": "",
                "country": "Norway",
                "state_code": "NO.20",
                "country_code": "NO",
                "city_code": "Hammerfest",
            },
            "source": "NTB",
            "text": "HAMMERFEST, Sep 13  -",
        },
        "genre": [
            {"qcode": "genre code", "name": "genre name"},
        ],
        "anpa_category": [
            {"name": "Omtaletjenesten", "qcode": "o", "language": "nb-NO"},
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
                    "original": {
                        "href": "http://scanpix.no/spWebApp/previewimage/sdl/preview_big/test_id.jpg",
                        "mimetype": "image/jpeg",
                    },
                    "thumbnail": {
                        "href": "http://preview.scanpix.no/thumbs/tb/4/33/test_id.jpg"
                    },
                    "viewImage": {
                        "href": "http://scanpix.no/spWebApp/previewimage/sdl/preview/test_id.jpg"
                    },
                },
                "source": "feature_source",
                "fetch_endpoint": "scanpix",
                "type": "picture",
                "versioncreated": datetime(2023, 3, 1, 12, 10, 0),
                "description_text": "test feature media",
                "subject": [
                    {
                        "parent": "05000000",
                        "scheme": None,
                        "name": "further education",
                        "qcode": "05002000",
                    },
                ],
            },
        },
        "extra": {
            "ntb_pub_name": "test ntb_pub_name",
        },
    }

    def setUp(self):
        super().setUp()
        self.formatter = NTBNINJSFormatter()
        with open(
            pathlib.Path(__file__).parent.parent.parent.parent.joinpath(
                "data/vocabularies.json"
            )
        ) as json_file:
            json_cvs = json.load(json_file)
            for cv in json_cvs:
                if cv.get("_id") == "place_custom":
                    self.app.data.insert("vocabularies", [cv])

    def format(self, updates=None):
        article = self.article.copy()
        if updates:
            article.update(updates)
        _, doc = self.formatter.format(article, {"name": "Test Subscriber"})[0]
        return json.loads(doc)

    def test_format_type(self):
        self.assertEqual("ntb_ninjs", self.formatter.format_type)

    def test_format_item(self):
        ninjs = self.format()
        assoc = ninjs.pop("associations")
        expected_item = {
            "uri": "123",
            "version": "1",
            "type": "text",
            "versioncreated": "2022-08-09T13:38:58+0000",
            "language": "nb-NO",
            "urgency": 3,
            "slugline": "test custom media2",
            "profile": "5ba11fec0d6f1301ac3cbd14",
            "people": [
                {
                    "name": "Hanjigeer",
                    "rel": "Ming dynasty person CBDB = 124590",
                    "literal": "f1d109e7-a5ae-3f7c-8a1d-5bce4a70bf64",
                    "uri": "http://www.wikidata.org/entity/Q45489119",
                }
            ],
            "organisations": [
                {
                    "name": "Events DC",
                    "rel": "Events DC is a semi-public company in Washington, D",
                    "literal": "4e42b5e7-bfbe-3c2b-9188-d263e8a147e2",
                    "uri": "http://www.wikidata.org/entity/Q16837590",
                }
            ],
            "events": [
                {
                    "name": "Noise Eve",
                    "rel": "An event for testing",
                    "literal": "23333-4ff44ff-fkkf4-kfkk444",
                    "uri": "http://www.wikidata.org/entity/Q72065689",
                }
            ],
            "objects": [
                {
                    "name": "Tata LPT 613",
                    "rel": "kjøretøymodell",
                    "literal": "9227b7fa-92c0-3593-a3b7-96a84deedf75",
                    "uri": "http://www.wikidata.org/entity/Q12072602",
                }
            ],
            "headlines": [
                {"value": "custom media field multi", "contenttype": "text/plain"}
            ],
            "descriptions": [
                {"value": "abstract this is", "contenttype": "text/plain"}
            ],
            "bodies": [
                {
                    "charcount": 162,
                    "wordcount": 29,
                    "value": TEST_BODY_EXPECTED,
                    "contenttype": "text/html",
                }
            ],
            "subjects": [
                {"name": "olje- og gassindustri", "uri": "topics:20000550"},
                {
                    "name": "Olje",
                    "uri": "imatrics_topic:66417b95-3ad5-35c3-8b5a-6dec0d4e0946",
                },
                {"name": "matlaging", "uri": "topics:20001253"},
                {"name": "Fritid", "uri": "subject_custom:10000000"},
            ],
            "altids": [
                {"role": "GUID", "value": self.article["guid"]},
                {"role": "NTB-ID", "value": "NTB{}".format(FAMILY_ID)},
                {"role": "DOC-ID", "value": "NTB{}_03".format(FAMILY_ID)},
            ],
            "places": [
                {
                    "name": "Gjerdrum",
                    "uri": "http://www.wikidata.org/entity/Q57084",
                    "literal": "Q57084",
                    "county-dist": "Gjerdrum",
                    "state-prov": "Viken",
                },
                {
                    "name": "Global",
                    "literal": "Global",
                },
                {
                    "name": "Genève",
                    "literal": "34017822-d341-3826-ab94-71d226d639c4",
                },
            ],
            "taglines": [
                "admin@example.com",
                "foo@bar.com",
            ],
            "located": "Hammerfest",
            "genre": [
                {"code": "genre code", "name": "genre name"},
            ],
            "service": [
                {"name": "Omtaletjenesten", "code": "o"},
            ],
            "infosources": [{"name": "NTB"}],
            "copyrightholder": "NTB",
            "by": "byline",
            "NTBKilde": "test ntb_pub_name",
        }

        self.assertEqual(ninjs, expected_item)

        self.assertEqual(
            assoc,
            [
                {
                    "name": "featuremedia",
                    "altids": [
                        {"role": "GUID", "value": "test_id"},
                    ],
                    "descriptions": [
                        {"contenttype": "text/plain", "value": "test feature media"},
                    ],
                    "uri": "test_id",
                    "headlines": [
                        {"contenttype": "text/plain", "value": "feature headline"},
                    ],
                    "pubstatus": "usable",
                    "taglines": [],
                    "type": "picture",
                    "version": "1",
                    "versioncreated": "2023-03-01T12:10:00+0000",
                    "subjects": [
                        {"name": "further education", "uri": "topics:05002000"},
                    ],
                    "copyrightholder": "NTB",
                }
            ],
        )

    def test_planning_ids(self):
        self.app.data.insert(
            "assignments",
            [
                {
                    "_id": "assignment-id",
                    "coverage_item": self.article["guid"],
                    "planning_item": "planning-id",
                },
            ],
        )
        self.app.data.insert(
            "planning",
            [
                {"_id": "planning-id", "event_item": "event-id"},
            ],
        )

        ninjs = self.format()

        self.assertIn(
            {"role": "PLANNING-ID", "value": "planning-id"},
            ninjs["altids"],
        )

        self.assertIn(
            {"role": "EVENT-ID", "value": "event-id"},
            ninjs["altids"],
        )

    def test_empty_assocations_renditions(self):
        ninjs = self.format({"associations": {"foo": None}})
        assert "associations" not in ninjs, ninjs.get("associations")

    def test_publish_table(self):
        ninjs = self.format(
            {
                "fields_meta": text_item_with_table["fields_meta"],
                "body_html": text_item_with_table["body_html"],
                "body_footer": "",
            }
        )
        assert "<table>" in ninjs["bodies"][0]["value"]
        assert (
            text_item_with_table["body_html"].replace("&nbsp;", " ")
            == ninjs["bodies"][0]["value"]
        )

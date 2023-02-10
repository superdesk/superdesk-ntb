import json
import pathlib

from unittest import mock
from ntb.publish.ntb_ninjs import NTBNINJSFormatter
from superdesk.tests import TestCase


FAMILY_ID = "abcd"


@mock.patch(
    "superdesk.publish.subscribers.SubscribersService.generate_sequence_number",
    lambda self, subscriber: 1,
)
class Ninjs2FormatterTest(TestCase):
    maxDiff = None
    article = {
        "_id": "5ba1224e0d6f13056bd82d50",
        "family_id": FAMILY_ID,
        "rewrite_sequence": 3,
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
        "abstract": "<p>abstract thi sis</p>",
        "body_html": "<p>Test body html field</p>",
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
    }

    def setUp(self):
        self.formatter = NTBNINJSFormatter()

    def test_format_type(self):
        self.assertEqual("ntb_ninjs", self.formatter.format_type)

    def test_format_item(self):
        with open(pathlib.Path(__file__).parent.parent.parent.parent.joinpath("data/vocabularies.json")) as json_file:
            json_cvs = json.load(json_file)
            for cv in json_cvs:
                if cv.get("_id") == "place_custom":
                    self.app.data.insert("vocabularies", [cv])
        seq, doc = self.formatter.format(self.article, {"name": "Test Subscriber"})[0]
        ninjs = json.loads(doc)
        expected_item = {
            "guid": "123",
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
                {"value": "abstract thi sis", "contenttype": "text/plain"}
            ],
            "bodies": [
                {
                    "charcount": 20,
                    "wordcount": 4,
                    "value": "<p>Test body html field</p>",
                    "contenttype": "text/plain",
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
                    "literal": "b564b1e1-1a99-324e-b643-88e5398305c6",
                    "countydist": "Gjerdrum",
                },
                {
                    "name": "Global",
                    "literal": "Global",
                },
            ],
            "taglines": [
                "admin@example.com",
                "foo@bar.com",
            ],
            "located": "Hammerfest",
        }

        self.assertEqual(ninjs, expected_item)

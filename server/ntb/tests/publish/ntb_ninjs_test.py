from unittest import mock
from ntb.publish.ntb_ninjs import NTBNINJSFormatter
from superdesk.tests import TestCase
import json


@mock.patch(
    "superdesk.publish.subscribers.SubscribersService.generate_sequence_number",
    lambda self, subscriber: 1,
)
class Ninjs2FormatterTest(TestCase):
    article = {
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
        ],
        "versioncreated": "2022-08-09T13:38:58+0000",
        "rewrite_sequence": 1,
        "language": "nb-NO",
        "body_footer": "footer text",
    }

    def setUp(self):
        self.formatter = NTBNINJSFormatter()

    def test_format_type(self):
        self.assertEqual("ntb_ninjs", self.formatter.format_type)

    def test_format_item(self):
        self.maxDiff = None
        seq, doc = self.formatter.format(self.article, {"name": "Test Subscriber"})[0]
        ninjs = json.loads(doc)
        expected_item = {
            "guid": "123",
            "version": "1",
            "type": "text",
            "versioncreated": "2022-08-09T13:38:58+0000",
            "language": "nb-NO",
            "headline": "custom media field multi",
            "slugline": "test custom media2",
            "rewrite_sequence": 1,
            "place": [
                {"name": "Gjerdrum", "code": "b564b1e1-1a99-324e-b643-88e5398305c6"}
            ],
            "profile": "5ba11fec0d6f1301ac3cbd14",
            "priority": 5,
            "subject": [
                {
                    "code": "20000550",
                    "name": "olje- og gassindustri",
                    "scheme": "topics",
                },
                {
                    "code": "66417b95-3ad5-35c3-8b5a-6dec0d4e0946",
                    "name": "Olje",
                    "scheme": "imatrics_topic",
                },
                {"code": "20001253", "name": "matlaging", "scheme": "topics"},
                {"code": "10000000", "name": "Fritid", "scheme": "subject_custom"},
            ],
            "people": [
                {
                    "name": "Hanjigeer",
                    "rel": "Ming dynasty person CBDB = 124590",
                    "qcode": "f1d109e7-a5ae-3f7c-8a1d-5bce4a70bf64",
                    "source": "imatrics",
                }
            ],
            "organisations": [
                {
                    "name": "Events DC",
                    "rel": "Events DC is a semi-public company in Washington, D",
                    "qcode": "4e42b5e7-bfbe-3c2b-9188-d263e8a147e2",
                    "source": "imatrics",
                }
            ],
        }
        self.assertEqual(ninjs, expected_item)

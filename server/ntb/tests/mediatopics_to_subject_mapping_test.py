import ntb
import json
import copy
import flask

from unittest import TestCase
from unittest.mock import patch
from ntb.publish.ntb_nitf import NTBNITFFormatter

from ntb.tests.mock import resources
from ntb.mediatopics_to_subject_mapping import populate_subject


class MediatopicsToSubjectMappingTestCase(TestCase):
    item = {
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
                "name": "fritid",
                "qcode": "20000538",
                "source": "imatrics",
                "scheme": "topics",
            },
        ],
    }

    def setUp(self) -> None:
        self.app = flask.Flask(__name__)
        self.app.cache = None
        self.app.config.from_object("settings")
        self.ctx = self.app.app_context()
        self.ctx.push()
        return super().setUp()

    def tearDown(self) -> None:
        self.ctx.pop()
        return super().tearDown()

    @patch("superdesk.resources", resources)
    def test_mapping(self, *mocks):
        item = copy.deepcopy(self.item)

        populate_subject(None, item, foo="bar")
        self.assertEqual(7, len(item["subject"]))

        self.assertEqual("10004000", item["subject"][4]["qcode"])
        self.assertEqual(ntb.SUBJECTCODES_CV, item["subject"][4]["scheme"])

        self.assertEqual("10000000", item["subject"][5]["qcode"])
        self.assertEqual(ntb.SUBJECTCODES_CV, item["subject"][5]["scheme"])

    @patch("superdesk.resources", resources)
    def test_mapping_to_nitf(self, *mocks):
        item = {
            "subject": [
                {
                    "name": "fotball",
                    "qcode": "20001065",
                    "source": "imatrics",
                    "altids": {
                        "imatrics": "e5125b3b-2a85-35d3-af37-ff7a3a671f2a",
                        "medtop": "20001065",
                        "wikidata": "Q2736",
                    },
                    "parent": "20000822",
                    "scheme": "topics",
                    "aliases": [],
                    "original_source": None,
                },
                {
                    "name": "sport",
                    "qcode": "15000000",
                    "source": "imatrics",
                    "altids": {
                        "imatrics": "d5dac14d-60d6-3695-8d78-e9fcd4158c5f",
                        "medtop": "15000000",
                        "wikidata": "Q349",
                    },
                    "parent": None,
                    "scheme": "topics",
                    "aliases": [],
                    "original_source": None,
                },
                {
                    "name": "idrettsdisiplin",
                    "qcode": "20000822",
                    "source": "imatrics",
                    "altids": {
                        "imatrics": "a3185c0d-c2af-3974-8573-6bb5d67d7989",
                        "medtop": "20000822",
                        "wikidata": "Q2312410",
                    },
                    "parent": "15000000",
                    "scheme": "topics",
                    "aliases": [],
                    "original_source": None,
                },
                {
                    "name": "Arkeologi",
                    "qcode": "01001000",
                    "parent": "01000000",
                    "scheme": "subject_custom",
                },
            ]
        }
        populate_subject(None, item)
        NTBNITFFormatter()._populate_metadata(item)
        print(json.dumps(item["subject"], indent=2))
        sports = [subj for subj in item["subject"] if subj["name"].lower() == "sport"]
        self.assertEqual(2, len(sports))

import ntb
import flask

from unittest import TestCase
from unittest.mock import patch
from superdesk.cache import cache

from ntb.tests.mock import resources
from ntb.mediatopics_to_subject_mapping import populate_subject


class MediatopicsToSubjectMappingTestCase(TestCase):
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
            ],
        }

        populate_subject(None, item, foo="bar")
        self.assertEqual(5, len(item["subject"]))

        self.assertEqual("10014000", item["subject"][3]["qcode"])
        self.assertEqual(ntb.SUBJECTCODES_CV, item["subject"][3]["scheme"])

        self.assertEqual("10000000", item["subject"][4]["qcode"])
        self.assertEqual(ntb.SUBJECTCODES_CV, item["subject"][4]["scheme"])

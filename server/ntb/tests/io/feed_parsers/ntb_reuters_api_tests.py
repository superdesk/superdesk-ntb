from ntb.io.feed_parsers.ntb_reuters_parser import NTBReutersFeedParser
from superdesk.tests import TestCase
import os
import json
from apps.prepopulate.app_populate import AppPopulateCommand
import datetime
from superdesk import utc


class NTBReutersFeedParserTests(TestCase):

    filename = "reutersapi_item.json"

    def setUp(self):
        super().setUp()
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(
            os.path.join(dirname, "../../fixtures", self.filename)
        )

        # we need to prepopulate vocabularies to get qcodes
        voc_file = os.path.normpath(
            os.path.join(dirname, "../../../../data", "vocabularies.json")
        )
        AppPopulateCommand().run(voc_file)

        self.parser = NTBReutersFeedParser()
        with open(fixture, "rb") as f:
            data = json.loads(f.read().decode("utf-8", "ignore"))
            self.items = self.parser.parse(data)

    def test_item(self):
        item = self.items[0]
        self.assertEqual(item["guid"], "tag:reuters.com,2023:newsml_RC2EQZ9KEA2R")
        self.assertEqual(item["type"], "text")
        self.assertEqual(item["state"], "ingested")
        self.assertEqual(
            item["headline"],
            "Footsteps are seen in a landfill contaminated with arsenic, in the village of Lojane",
        )
        self.assertEqual(item["slugline"], "NORTH MACEDONIA-POLLUTION/")
        self.assertEqual(
            item["versioncreated"],
            datetime.datetime(2023, 3, 24, 11, 5, 25, tzinfo=utc.utc),
        )
        self.assertEqual(
            item["firstcreated"],
            datetime.datetime(2023, 3, 24, 11, 5, 25, tzinfo=utc.utc),
        )
        self.assertEqual(item["language"], "en")
        self.assertEqual(item["urgency"], 4)
        self.assertEqual(
            item["subject"],
            [
                {
                    "name": "Natur og miljø",
                    "qcode": "06000000",
                    "scheme": "subject_custom",
                },
                {"name": "Fotball", "qcode": "15054000", "scheme": "subject_custom"},
                {"qcode": "Sport", "name": "Sport", "scheme": "category"},
            ],
        )

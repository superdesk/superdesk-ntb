import os
from ntb.io.feed_parsers import ntb_nitf

from superdesk import config
from superdesk.tests import TestCase
from superdesk.etree import etree
from apps.prepopulate.app_populate import AppPopulateCommand
import ntb


class XMLParserTestCase(TestCase):

    filename = "afp.xml"

    def setUp(self):
        super().setUp()
        # we need to prepopulate vocabularies to get qcodes
        voc_file = os.path.join(
            os.path.abspath(os.path.dirname(os.path.dirname(ntb.__file__))),
            "data",
            "vocabularies.json",
        )
        AppPopulateCommand().run(voc_file)

        setattr(config, "NITF_MAPPING", ntb_nitf.NITF_MAPPING)

        self._run_parse()

    def _run_parse(self):
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(os.path.join(dirname, "../fixtures", self.filename))
        provider = {"_id": "123123", "name": "Test"}

        with open(fixture, "rb") as f:
            self.xml = f.read()
            self.xml_root = etree.fromstring(self.xml)
            self.item = self.parser.parse(self.xml_root, provider)

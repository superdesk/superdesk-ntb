import os
import settings

from superdesk import config
from superdesk.tests import TestCase
from superdesk.etree import etree
from superdesk.vocabularies.commands import VocabulariesPopulateCommand


class XMLParserTestCase(TestCase):

    filename = 'afp.xml'

    def setUp(self):
        super().setUp()
        # we need to prepopulate vocabularies to get qcodes
        voc_file = os.path.join(os.path.abspath(os.path.dirname(settings.__file__)), "data/vocabularies.json")
        VocabulariesPopulateCommand().run(voc_file)

        # settings are needed in order to get into account NITF_MAPPING
        for key in dir(settings):
            if key.isupper():
                setattr(config, key, getattr(settings, key))

        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(os.path.join(dirname, '../fixtures', self.filename))
        provider = {'name': 'Test'}
        with open(fixture, 'rb') as f:
            self.xml = f.read()
            self.xml_root = etree.fromstring(self.xml)
            self.item = self.parser.parse(self.xml_root, provider)

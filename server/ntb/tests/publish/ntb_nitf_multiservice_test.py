
from unittest import TestCase
from ntb.publish.ntb_nitf_multiservice import NTBNITFMultiServiceMediaFormatter


class MultiserviceMediaNITFFormatterTestCase(TestCase):

    def test_scanpix_original_href(self):
        formatter = NTBNITFMultiServiceMediaFormatter()
        data = {
            'type': 'picture',
            'fetch_endpoint': 'scanpix',
            'renditions': {
                'original': {'href': 'http://example.com'},
            },
        }

        self.assertEqual(data['renditions']['original']['href'], formatter._get_media_source(data))

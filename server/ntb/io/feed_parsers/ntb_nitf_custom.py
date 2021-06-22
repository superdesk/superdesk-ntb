import superdesk
from superdesk.io.feed_parsers.nitf import NITFFeedParser
from superdesk.io.registry import register_feed_parser
from superdesk.errors import ParserError
from superdesk.text_utils import get_word_count
from superdesk.metadata.item import CONTENT_TYPE, ITEM_TYPE

SETTINGS_MAPPING_PARAM = "NITF_MAPPING"


class NTBNITFCustomFeedParser(NITFFeedParser):
    """
    NITF Parser extension for NTB custom NITF parser to store place and dateline
    """

    NAME = "ntb_nitf_custom"

    label = "NTB NITF Custom"

    def get_place(self, xml):
        places = []
        qcodes = []
        voc_places = superdesk.get_resource_service("vocabularies").find_one(req=None, _id="place_custom")["items"]

        for elem in xml.findall("head/docdata/evloc"):
            qcode = elem.attrib.get("county-dist")
            if qcode and qcode not in qcodes:
                qcodes.append(qcode)

        for place in voc_places:
            place["scheme"] = "place_custom"
            if place.get("qcode") in qcodes or place.get("ntb_qcode") in qcodes:
                places.append(place)

        return places

    def parse(self, xml, provider=None):
        self.xml = xml
        item = {
            ITEM_TYPE: CONTENT_TYPE.TEXT,  # set the default type.
        }
        try:
            self.do_mapping(item, xml, SETTINGS_MAPPING_PARAM)
            elem = xml.find("body/body.head/dateline")
            if elem is not None:
                city = elem.text if elem.text else elem.attrib.get("location")
                if city:
                    self.set_dateline(item, city=city)

            item.setdefault(
                "word_count", get_word_count(item["body_html"], no_html=True)
            )
        except Exception as ex:
            raise ParserError.nitfParserError(ex, provider)
        return item


register_feed_parser(NTBNITFCustomFeedParser.NAME, NTBNITFCustomFeedParser())

from typing import Dict, List
from superdesk import get_resource_service
from superdesk.publish.formatters.ninjs_formatter import NINJSFormatter

from . import utils


def format_array_value(assoc, name):
    output = {**assoc}
    output.update(name=name)
    convert_dicts_to_lists(output)
    return output


def convert_dicts_to_lists(ninjs):
    for field in ("renditions", "associations"):
        if ninjs.get(field):
            ninjs[field] = [
                format_array_value(value, key)
                for key, value
                in ninjs[field].items()
            ]


class NTBNINJSFormatter(NINJSFormatter):
    """NTB NINJS formatter

    .. versionadded:: 2.0

    Extending :py:class:`NINJSFormatter` to avoid breaking changes.

    """

    name = "NTB NINJS"
    type = "ntb_ninjs"

    def __init__(self):
        super().__init__()
        self.format_type = "ntb_ninjs"
        self._places = None

    def _transform_to_ninjs(self, article, subscriber, recursive=True):
        ninjs = super()._transform_to_ninjs(article, subscriber, recursive)

        imatrics_fields = {
            "people": "person",
            "organisations": "organisation",
            "events": "event",
            "objects": "object",
        }

        for field, value in imatrics_fields.items():
            ninjs[field] = self.format_imatrics(article, value)

        if ninjs.get("headline"):
            ninjs["headlines"] = self.format_headlines(article)

        if ninjs.get("description_text"):
            ninjs["descriptions"] = self.format_descriptions(ninjs)

        if ninjs.get("body_html"):
            ninjs["bodies"] = self.format_bodies(ninjs)

        if ninjs.get("subject"):
            ninjs["subjects"] = self.format_subjects(ninjs)

        if ninjs.get("place"):
            ninjs["places"] = ninjs["place"]

        # removed items which mapped according to Ninjs v2 properties
        ninjs_properties = [
            "headlines",
            "uri",
            "type",
            "profile",
            "version",
            "firstcreated",
            "versioncreated",
            "pubstatus",
            "contentcreated",
            "embargoed",
            "urgency",
            "copyrightholder",
            "copyrightnotice",
            "usageterms",
            "ednote",
            "guid",
            "language",
            "descriptions",
            "bodies",
            "headlines",
            "people",
            "organisations",
            "places",
            "subjects",
            "events",
            "objects",
            "title",
            "by",
            "slugline",
            "located",
            "renditions",
            "associations",
            "altids",
            "trustindicators",
            "standard",
            "genre",
            "rightsinfo",
            "service",
        ]

        for key in list(ninjs.keys()):
            if key not in ninjs_properties or ninjs[key] is None:
                ninjs.pop(key)

        ninjs["altids"] = [
            {"role": "GUID", "value": article["guid"]},
        ]

        if article.get("family_id"):
            ninjs["altids"].extend([
                {"role": "NTB-ID", "value": utils.get_ntb_id(article)},
                {"role": "DOC-ID", "value": utils.get_doc_id(article)},
            ])

        ninjs["taglines"] = []
        if article.get("sign_off"):
            for tagline in article["sign_off"].split("/"):
                ninjs["taglines"].append(tagline.strip())

        if recursive:  # should only run at the end, so do this on top level item only
            convert_dicts_to_lists(ninjs)

        return ninjs

    def _format_place(self, article) -> List[Dict]:
        places = []
        for place in article["place"]:
            ninjs_place = {
                "name": place.get("name"),
                "literal": place.get("qcode"),
            }

            cv_place = self.places.get(place["qcode"])
            if cv_place:
                if cv_place.get("ntb_qcode"):
                    ninjs_place["county-dist"] = cv_place["ntb_qcode"]
                if cv_place.get("ntb_parent"):
                    ninjs_place["state-prov"] = cv_place["ntb_parent"]

            if place.get("altids") and place["altids"].get("wikidata"):
                ninjs_place["uri"] = "http://www.wikidata.org/entity/{}".format(place["altids"]["wikidata"])
            places.append(ninjs_place)
        return places

    def _format_rendition(self, rendition):
        print("IN", rendition)
        formatted = super()._format_rendition(rendition)
        if formatted.get("mimetype"):
            formatted["contenttype"] = formatted.pop("mimetype")
        return formatted

    def format_imatrics(self, article, value):
        fields_data = []
        if article.get(value):
            article_data = article[value]
            for item in article_data:
                altids = item.get("altids")
                data = {
                    "name": item.get("name"),
                    "rel": item.get("description"),
                    "literal": item.get("qcode"),
                }
                if altids.get("wikidata"):
                    id = altids["wikidata"]
                    data["uri"] = f"http://www.wikidata.org/entity/{id}"
                else:
                    qcode = item["qcode"]
                    data["uri"] = f"imatrics:{qcode}"
                fields_data.append(data)
            return fields_data

    def format_headlines(self, article):
        return [{"value": article.get("headline"), "contenttype": "text/plain"}]

    def format_descriptions(self, ninjs):
        return [{"value": ninjs.get("description_text"), "contenttype": "text/plain"}]

    def format_bodies(self, ninjs):
        return [
            {
                "charcount": ninjs.get("charcount"),
                "wordcount": ninjs.get("wordcount"),
                "value": ninjs.get("body_html"),
                "contenttype": "text/plain",
            }
        ]

    def format_subjects(self, ninjs):
        subjects = []
        for item in ninjs["subject"]:
            subjects.append(
                {
                    "name": item["name"],
                    "uri": "{scheme}:{code}".format(
                        scheme=item["scheme"], code=item["code"]
                    ),
                }
            )
        return subjects

    @property
    def places(self):
        if self._places is None:
            places = get_resource_service("vocabularies").get_items("place_custom")
            self._places = {p["qcode"]: p for p in places}
        return self._places

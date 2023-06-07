import lxml.etree as etree

from flask import g
from typing import Dict, List
from lxml.html import HTMLParser
from superdesk import get_resource_service
from superdesk.etree import clean_html, to_string
from superdesk.publish.formatters.ninjs_formatter import NINJSFormatter
from superdesk.text_utils import get_char_count, get_word_count

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
        elif field in ninjs:
            ninjs.pop(field)


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

        if article.get("body_html"):
            ninjs["bodies"] = self.format_bodies(article)

        if ninjs.get("subject"):
            ninjs["subjects"] = self.format_subjects(ninjs)

        if ninjs.get("place"):
            ninjs["places"] = ninjs["place"]

        if ninjs.get("guid"):
            ninjs.setdefault("uri", ninjs["guid"])

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
            "associations",
            "altids",
            "trustindicators",
            "standard",
            "genre",
            "rightsinfo",
            "service",
            "infosources",
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

        if article.get("assignment_id"):
            self._format_planning_ids(ninjs, article)

        ninjs["taglines"] = []
        if article.get("sign_off"):
            for tagline in article["sign_off"].split("/"):
                ninjs["taglines"].append(tagline.strip())

        if article.get("type") == "text":
            ninjs["infosources"] = [
                {"name": utils.get_distributor(article)},
            ]

        if article.get("byline"):
            ninjs["by"] = article["byline"]

        if recursive:  # should only run at the end, so do this on top level item only
            convert_dicts_to_lists(ninjs)

        ninjs["copyrightholder"] = "NTB"

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

    def format_bodies(self, article):
        html, _ = utils.format_body_content(article)
        parser = HTMLParser(recover=True, remove_blank_text=True)
        try:
            html_tree = etree.fromstring(html, parser)
        except Exception as e:
            raise ValueError("Can't parse body_html content: {}".format(e))
        html_tree_clean = clean_html(html_tree)
        html = to_string(html_tree_clean, method="html", remove_root_div=True)
        return [
            {
                "charcount": get_char_count(html),
                "wordcount": get_word_count(html),
                "value": html,
                "contenttype": "text/html",
            }
        ]

    def format_subjects(self, ninjs):
        subjects = []
        for item in ninjs["subject"]:
            subjects.append(
                {
                    "name": item["name"],
                    "uri": "{scheme}:{code}".format(
                        scheme=item.get("scheme") or "topics", code=item["code"]
                    ),
                }
            )
        return subjects

    @property
    def places(self):
        if getattr(g, "_places", None) is None:
            places = get_resource_service("vocabularies").get_items("place_custom")
            g._places = {p["qcode"]: p for p in places}
        return getattr(g, "_places")

    def _format_planning_ids(self, ninjs, article):
        assignment = get_resource_service("assignments").find_one(req=None, _id=article["assignment_id"])
        if assignment and assignment.get("planning_item"):
            ninjs.setdefault("altids", []).append({
                "role": "PLANNING-ID",
                "value": assignment["planning_item"],
            })
            planning = get_resource_service("planning").find_one(req=None, _id=assignment["planning_item"])
            if planning and planning.get("event_item"):
                ninjs["altids"].append({
                    "role": "EVENT-ID",
                    "value": planning["event_item"],
                })

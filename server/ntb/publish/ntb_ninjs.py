from superdesk.publish.formatters.ninjs_formatter import NINJSFormatter


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
            "genres",
            "rightsinfo",
        ]
        for key in list(ninjs.keys()):
            if key not in ninjs_properties:
                ninjs.pop(key)

        return ninjs

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

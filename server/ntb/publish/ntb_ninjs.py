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

        ninjs["people"] = self.format_people(article)

        ninjs["organisations"] = self.format_organisations(article)

        if ninjs.get("headline"):
            ninjs["headlines"] = self.format_headlines(article)

        if ninjs.get("description_text"):
            ninjs["descriptions"] = self.format_descriptions(ninjs)

        if ninjs.get("body_html"):
            ninjs["bodies"] = self.format_bodies(ninjs)

        if ninjs.get("subject"):
            ninjs["subjects"] = self.format_subjects(ninjs)

        # removable items which mapped according to Ninjs v2
        removable_items = [
            "body_html",
            "description_html",
            "description_text",
            "charcount",
            "wordcount",
            "readtime",
            "headline",
            "subject",
        ]
        for item in removable_items:
            ninjs.pop(item)

        return ninjs

    def format_people(self, article):
        peoples = []
        if article.get("person"):
            persons = article["person"]
            for item in persons:
                altids = item.get("altids")
                peoples.append(
                    {
                        "name": item.get("name"),
                        "rel": item.get("description"),
                        "qcode": item.get("qcode")
                        if altids.get("wikidata") is None
                        else altids["wikidata"],
                        "source": item.get("source"),
                    }
                )
            return peoples

    def format_organisations(self, article):
        organisations = []
        if article.get("organisation"):
            items = article["organisation"]
            for item in items:
                altids = item.get("altids")
                organisations.append(
                    {
                        "name": item.get("name"),
                        "rel": item.get("description"),
                        "qcode": item.get("qcode")
                        if altids.get("wikidata") is None
                        else altids["wikidata"],
                        "source": item.get("source"),
                    }
                )
            return organisations

    def format_headlines(self, article):
        return [{"value": article.get("headline")}]

    def format_descriptions(self, ninjs):
        return [{"value": ninjs.get("description_text")}]

    def format_bodies(self, ninjs):
        return [
            {
                "charcount": ninjs.get("charcount"),
                "wordcount": ninjs.get("wordcount"),
                "value": ninjs.get("body_html"),
            }
        ]

    def format_subjects(self, ninjs):
        subjects = []
        for item in ninjs["subject"]:
            subjects.append({"name": item["name"], "uri": item["code"]})
        return subjects

from superdesk.publish.formatters.ninjs_formatter import NINJS2Formatter


class NTBNINJSFormatter(NINJS2Formatter):
    """NINJS formatter v2

    .. versionadded:: 2.0

    Extending :py:class:`NINJSFormatter` to avoid breaking changes.

    *Changes*:

    - user ``correction_sequence`` for ``version`` field, so it's 1, 2, 3, ... in the output
    - add ``rewrite_sequence`` field
    - add ``rewrite_of`` field

    """

    name = "NTB NINJS"
    type = "ntb_ninjs"

    def __init__(self):
        super().__init__()
        self.format_type = "ntb_ninjs"

    def _transform_to_ninjs(self, article, subscriber, recursive=True):
        ninjs = super()._transform_to_ninjs(article, subscriber, recursive)
        ninjs["version"] = str(article.get("correction_sequence", 1))

        # mapping Imatrics
        if article.get("person"):
            ninjs["people"] = self.format_people(article)

        if article.get("organisations"):
            ninjs["organisations"] = self.format_organisations(article)

        return ninjs

    def format_people(self, article):
        peoples = []
        persons = article["person"]
        for item in persons:
            peoples.append(
                {
                    "name": item.get("name"),
                    "rel": item.get("description"),
                    "qcode": item.get("qcode"),
                    "source": item.get("source"),
                }
            )
        return peoples

    def format_organisations(self, article):
        organisations = []
        items = article["organisations"]
        for item in items:
            organisations.append(
                {
                    "name": item.get("name"),
                    "rel": item.get("description"),
                    "qcode": item.get("qcode"),
                    "source": item.get("source"),
                }
            )
        return organisations

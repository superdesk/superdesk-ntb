from flask import current_app as app
from superdesk.text_checkers.ai.imatrics import IMatrics


def callback(item, **kwargs):
    imatrics = IMatrics(app)
    parsed = imatrics.analyze(item)
    if parsed:
        for key, values in parsed.items():
            item.setdefault(key, [])
            for value in values:
                if qcode(value) not in map(qcode, item[key]):
                    item[key].append(value)
    return item


def qcode(value):
    return "{}:{}".format(value.get("scheme"), value.get("qcode"))


name = "iMatrics"
label = "Run iMatrics"
access_type = "backend"
action_type = "direct"

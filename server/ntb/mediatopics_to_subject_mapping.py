import ntb

from flask import current_app as app
from superdesk import get_resource_service
from superdesk.timer import timer
from superdesk.signals import item_publish
from ntb.mediatopics import get_mediatopics


def populate_subject(sender, item, **kwargs) -> None:
    topics = get_mediatopics(item)
    if not topics:
        return
    with timer("mediatopics:mapping"):
        mapping = _get_topics_mapping()
    subjects = []
    for topic in topics:
        subject = mapping.get(topic["qcode"])
        if subject:
            subjects.append(subject)

    for subject in subjects:
        if not any(
            s["qcode"] == subject["qcode"] and s.get("scheme") == subject.get("scheme")
            for s in item["subject"]
        ):
            item["subject"].append(subject)


def _get_topics_mapping():
    _topics_mapping = {}
    topics = get_resource_service("vocabularies").get_items(ntb.MEDIATOPICS_CV)
    subjects = get_resource_service("vocabularies").get_items(ntb.SUBJECTCODES_CV)
    for topic in topics:
        subject_code = app.config["MEDIATOPIC_SUBJECTCODE_MAPPING"].get(topic["qcode"])
        if not subject_code and topic.get("iptc_subject"):
            subject_code = topic["iptc_subject"]
        if not subject_code:
            continue
        for subject in subjects:
            if subject.get("qcode") == subject_code:
                _topics_mapping[topic["qcode"]] = subject
                break
    return _topics_mapping


def init_app(app):
    item_publish.connect(populate_subject)

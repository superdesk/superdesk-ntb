import superdesk

TOPICS_ID = 'topics'


def get_topics_lookup():
    topics_cv = superdesk.get_resource_service('vocabularies').find_one(req=None, _id=TOPICS_ID)
    return {
        topic['iptc_subject']: topic
        for topic in topics_cv['items']
        if topic.get('is_active') and topic.get('iptc_subject')
    }


def get_item_topics(subject, topics):
    item_topics = []
    for subj in subject:
        topic = topics.get(subj['qcode'])
        if topic:
            item_topics.append({
                'name': topic['name'],
                'qcode': topic['qcode'],
                'scheme': TOPICS_ID,
            })
    return item_topics


class UpdateTopicsScript():

    def __init__(self):
        self._topics = None

    @property
    def topics(self):
        if self._topics is None:
            self._topics = get_topics_lookup()
        return self._topics

    def __call__(self, item, updates):
        if not item.get("subject"):
            return
        subject = [subj for subj in item["subject"] if subj]  # filter out None
        for subj in subject:
            if subj.get("scheme") == TOPICS_ID:
                return
        try:
            item_topics = get_item_topics(subject, self.topics)
        except KeyError:
            return
        if item_topics:
            updates.update({'subject': subject + item_topics})

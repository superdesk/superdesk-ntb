import superdesk

TOPICS_ID = 'topics'


def get_topics_lookup():
    topics_cv = superdesk.get_resource_service('vocabularies').find_one(req=None, _id=TOPICS_ID)
    return {
        topic['iptc_subject']: topic
        for topic in topics_cv['items']
        if topic.get('is_active') and topic.get('iptc_subject')
    }


def get_item_topics(item, topics):
    item_topics = []
    for subj in item['subject']:
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

    def __call__(self, item, updates):
        if not item.get("subject"):
            return
        for subj in item["subject"]:
            if subj.get("scheme") == TOPICS_ID:
                return
        if self._topics is None:
            self._topics = get_topics_lookup()
        try:
            item_topics = get_item_topics(item, self._topics)
        except KeyError:
            return
        if item_topics:
            updates.update({'subject': item['subject'] + item_topics})

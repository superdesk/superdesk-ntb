
import time
import bson
import bson.errors

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


class MigrateTopicsCommand(superdesk.Command):
    """Migrate Topics"""

    option_list = [
        superdesk.Option('--loops', '-l', dest='loops', type=int, default=1000,
                         help='set iterations limit per resource'),
        superdesk.Option('--sleep', '-s', dest='sleep', type=float, default=2,
                         help='set for how long it will sleep between searches'),
    ]

    def run(self, loops, sleep):
        topics = get_topics_lookup()
        if not topics:
            print('no topics found')
            return

        query = {
            'bool': {
                'filter': {
                    'terms': {
                        'subject.qcode': list(topics.keys()),
                    },
                },
                'must_not': {
                    'term': {'subject.scheme': TOPICS_ID},
                },
            },
        }

        for resource in ('events', 'planning', 'archive', 'published', 'archived'):
            source = {'query': query}
            service = superdesk.get_resource_service(resource)

            print('updating', resource)
            for _ in range(loops):  # make sure this will finish one day
                items = list(service.search(source))
                if not items:
                    print('done.')
                    break
                for item in items:
                    try:
                        _id = bson.ObjectId(item['_id'])
                    except bson.errors.InvalidId:
                        _id = item['_id']
                    updates = {'subject': item['subject'] + get_item_topics(item, topics)}
                    service.system_update(_id, updates, item)
                print('.', end='')
                time.sleep(sleep)  # let elastic refresh before doing next search

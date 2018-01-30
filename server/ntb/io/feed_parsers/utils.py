
import superdesk

IPTC_SPORT_PREFIX = '15'
SPORT_CATEGORY = 'Sport'
DEFAULT_CATEGORY = 'Utenriks'
SUBJECT_CV = 'subject_custom'
SERVICE_CV = 'categories'
DEFAULT_SERVICE = 'n'


def ingest_category_from_subject(subjects):
    """Get default or sport category based on given subjects."""
    if not subjects:
        subjects = []
    if any([True for subject in subjects if subject.get('qcode', '').startswith(IPTC_SPORT_PREFIX)]):
        cat = SPORT_CATEGORY
    else:
        cat = DEFAULT_CATEGORY
    return {'qcode': cat, 'name': cat, 'scheme': 'category'}


def filter_missing_subjects(subjects):
    """Use labels from subject_custom cv and ignore missing qcodes."""
    if not subjects:
        subjects = []
    next_subjects = []
    cv = _get_cv(SUBJECT_CV)
    for item in cv['items']:
        if item.get('is_active'):
            for subject in subjects:
                if item.get('qcode') == subject.get('qcode'):
                    next_subjects.append({
                        'name': item['name'],
                        'qcode': item['qcode'],
                        'scheme': SUBJECT_CV,
                    })
    return next_subjects


def set_default_service(article):
    if article.get('anpa_category'):
        return
    cv = _get_cv(SERVICE_CV)
    if not cv:
        return
    active_items = [item for item in cv.get('items', []) if item.get('is_active')]
    if active_items:
        service = active_items[0]
        for item in active_items:
            if item.get('qcode') == DEFAULT_SERVICE:
                service = item
                break
        article['anpa_category'] = [
            {
                'name': service['name'],
                'qcode': service['qcode'],
            }
        ]


def _get_cv(_id):
    return superdesk.get_resource_service('vocabularies').find_one(req=None, _id=_id)

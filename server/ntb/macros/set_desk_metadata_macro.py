
from superdesk import get_resource_service


FIELD_SCHEME_MAP = {
    'subject': 'category',
    'genre': 'genre_custom',
    'anpa_category': None,
}


def callback(item, **kwargs):
    try:
        template_id = kwargs["desk"]["default_content_template"]
    except KeyError:
        return
    template = get_resource_service('content_templates').find_one(req=None, _id=template_id)
    if not template:
        return
    template_data = template.get("data") or {}
    for field, scheme in FIELD_SCHEME_MAP.items():
        item.setdefault(field, [])
        item[field] = [val for val in item[field] if val.get('scheme') != scheme]
        if template_data.get(field):
            for val in template_data[field]:
                if val.get('scheme') == scheme:
                    item[field].append(val)


name = 'Set Desk Metadata'
label = 'Set Desk Metadata'
access_type = 'frontend'
action_type = 'direct'

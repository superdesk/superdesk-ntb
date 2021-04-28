
import bson
import bson.errors
import superdesk

from .update_topics import UpdateTopicsScript
from .update_places import UpdatePlacesScript


RESOURCES = ('events', 'planning', 'archive', 'published', 'archived')

SCRIPTS = [
    ("topics", UpdateTopicsScript()),
    ("places", UpdatePlacesScript()),
]


def get_id(id):
    try:
        return bson.ObjectId(id)
    except bson.errors.InvalidId:
        return id


class UpdateItemsCommand(superdesk.Command):
    """Update Items"""

    option_list = [
        superdesk.Option('--resource', '-r', dest='resources', action='append', choices=RESOURCES),
        superdesk.Option('--last', '-l'),
    ]

    def run(self, resources=None, last=None):
        if not resources:
            resources = RESOURCES
        for resource in resources:
            print("updating {resource}".format(resource=resource))
            service = superdesk.get_resource_service(resource)
            last_id = None

            if last:
                last_item = service.find_one(req=None, _id=get_id(last))
                if not last_item:
                    print("skip resource {resource}".format(resource=resource))
                    continue
                print("continue from {last}".format(last=last))
                last_id = get_id(last_item['_id'])

            query = {}
            while True:
                if last_id:
                    query["_id"] = {"$gt": last_id}
                items = list(service.find(query, max_results=500).sort("_id", 1))
                if not items:
                    print("done.")
                    break
                for item in items:
                    _id = get_id(item['_id'])
                    if _id == last_id:
                        print("error: processing {_id} again".format(_id=last_id))
                        raise ValueError("Invalid id.")
                    last_id = _id
                    updates = {}
                    for _, script in SCRIPTS:
                        script(item, updates)
                    if updates:
                        print("update", resource, _id)
                        try:
                            service.system_update(_id, updates, item)
                        except Exception as err:
                            print("error", err, "updates", updates)
                    else:
                        print("ignore", resource, _id)

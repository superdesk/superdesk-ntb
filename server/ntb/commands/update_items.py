
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


class UpdateItemsCommand(superdesk.Command):
    """Update Items"""

    option_list = [
        superdesk.Option('--resource', '-r', dest='resources', action='append', choices=RESOURCES),
    ]

    def run(self, resources=None):
        if not resources:
            resources = RESOURCES
        for resource in resources:
            last_id = None
            service = superdesk.get_resource_service(resource)
            print("updating {resource}".format(resource=resource))
            query = {}
            while True:
                if last_id:
                    query["_id"] = {"$gt": last_id}
                items = list(service.find(query, max_results=500).sort("_id", 1))
                if not items:
                    print("done.")
                    break
                for item in items:
                    try:
                        _id = bson.ObjectId(item['_id'])
                    except bson.errors.InvalidId:
                        _id = item['_id']
                    if _id == last_id:
                        print("error: processing {_id} again".format(_id=last_id))
                        raise ValueError("Invalid id.")
                    last_id = _id
                    updates = {}
                    for _, script in SCRIPTS:
                        script(item, updates)
                    if updates:
                        print("update", _id, updates)
                        try:
                            service.system_update(_id, updates, item)
                        except Exception as err:
                            print("error: {error}".format(error=err))
                print(".", end="")

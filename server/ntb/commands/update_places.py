
import superdesk

CV_ID = "place_custom"


def fetch_places():
    places = {}
    items = superdesk.get_resource_service("vocabularies").get_items(_id=CV_ID)
    for item in items:
        places[item["ntb_qcode"]] = item
    return places


def get_item_place(item, places):
    return [
        places[place["qcode"]] if places.get(place["qcode"]) else place
        for place in item["place"]
    ]


class UpdatePlacesScript():

    def __init__(self):
        self._places = None

    def __call__(self, item, updates):
        if not item.get("place"):
            return
        for place in item["place"]:
            if place.get("scheme") == CV_ID:
                return
        if self._places is None:
            self._places = fetch_places()
        item_place = get_item_place(item, self._places)
        if item_place:
            updates["place"] = item_place


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
        if place and place.get("qcode")
    ]


class UpdatePlacesScript():

    def __init__(self):
        self._places = None

    @property
    def places(self):
        if self._places is None:
            self._places = fetch_places()
        return self._places

    def __call__(self, item, updates):
        if not item.get("place"):
            return
        for place in item["place"]:
            if place and place.get("scheme") == CV_ID:
                return
        item_place = get_item_place(item, self.places)
        if item_place and item_place != item["place"]:
            updates["place"] = item_place

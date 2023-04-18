import superdesk

from datetime import datetime, timedelta
from flask import current_app as app


class FixEventsCommand(superdesk.Command):
    """Fix events affected by moment timezone issue

    which were saved during summer time using the offset of winter time (or vice versa in Australia).
    """

    option_list = [
        superdesk.Option("--start", "-s", default="2023-03-26T01:00:00+00:00"),
        superdesk.Option("--end", "-e", default="2023-10-29T01:00:00+00:00"),
        superdesk.Option("--updated", "-u", default="2023-03-20T17:00:00+00:00"),
        superdesk.Option("--offset", "-o", default="-1"),
    ]

    def run(self, start, end, updated, offset):
        start = datetime.fromisoformat(start)
        end = datetime.fromisoformat(end)
        updated = datetime.fromisoformat(updated)
        offset = timedelta(hours=int(offset))

        app.logger.info(
            "Updating events from %s to %s not updated after %s", start, end, updated
        )

        query = {
            "dates.start": {
                "$gte": start,
                "$lt": end,
            },
            "dates.end": {"$gte": start, "$lt": end},
            "_updated": {
                "$lt": updated
            },  # ignore updated after the instance update, assuming the updates were to fix the dates
            "ingest_provider": {"$exists": 0},  # ignore ingested events
        }

        updated_count = 0
        events_service = superdesk.get_resource_service("events")
        for event in events_service.get_from_mongo(req=None, lookup=query):
            dates = event["dates"].copy()
            if dates["start"] > start:
                dates["start"] += offset
            if dates["end"] < end:
                dates["end"] += offset
            updates = {"dates": dates}

            events_service.update(event["_id"], updates, event)
            app.on_updated_events(updates, event)
            app.logger.info("Event updated: %s", event.get("name") or event.get("_id"))
            updated_count += 1

        app.logger.info("Updated %d events", updated_count)

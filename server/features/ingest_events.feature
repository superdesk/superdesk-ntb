Feature: Events ingest

    @ntb_vocabulary @auth @ntb_event_api_provider
    Scenario: Ingest NTB event API xml
        Given empty "events"
        When we get "/events"
        Then we get list with 0 items
        When we fetch events "0.xml,1.xml,2.xml,3.xml" from "ntb-events-api" NTB Events API provider
        When we get "/events"
        Then we get list with 8 items

    @ntb_vocabulary @auth @ntb_event_api_provider
    Scenario: Ingested events list does not contain ntb_id
        Given empty "events"
        When we get "/events"
        Then we get list with 0 items
        When we fetch events "0.xml,1.xml,2.xml,3.xml" from "ntb-events-api" NTB Events API provider
        When we get "/events"
        Then we get list without ntb_id

    @ntb_vocabulary @auth @ntb_event_api_provider
    Scenario: Ingested events are updated when feeding service restarted
        Given empty "events"
        When we get "/events"
        Then we get list with 0 items
        When we fetch events "0.xml,1.xml,2.xml,3.xml" from "ntb-events-api" NTB Events API provider
        When we get "/events"
        Then we get list with 8 items
        """
        {
            "_items": [
                {
                    "dates": {
                        "end": "2018-09-29T19:30:00+0000",
                        "start": "2018-09-29T16:30:00+0000",
                        "tz": "Europe/Oslo"
                    },
                    "state": "ingested",
                    "type": "event"
                },
                {
                    "dates": {
                        "end": "2018-10-24T18:45:00+0000",
                        "start": "2018-10-24T16:15:00+0000",
                        "tz": "Europe/Oslo"
                    },
                    "state": "ingested",
                    "type": "event"
                },
                {
                    "dates": {
                        "end": "2018-10-26T12:00:00+0000",
                        "start": "2018-10-26T10:30:00+0000",
                        "tz": "Europe/Oslo"
                    },
                    "state": "ingested",
                    "type": "event"
                },
                {
                    "dates": {
                        "end": "2018-10-27T12:00:00+0000",
                        "start": "2018-10-27T10:30:00+0000",
                        "tz": "Europe/Oslo"
                    },
                    "state": "ingested",
                    "type": "event"
                },
                {
                    "dates": {
                        "end": "2018-10-27T16:30:00+0000",
                        "start": "2018-10-27T15:00:00+0000",
                        "tz": "Europe/Oslo"
                    },
                    "state": "ingested",
                    "type": "event"
                },
                {
                    "dates": {
                        "end": "2018-10-28T12:15:00+0000",
                        "start": "2018-10-28T10:45:00+0000",
                        "tz": "Europe/Oslo"
                    },
                    "state": "ingested",
                    "type": "event"
                },
                {
                    "dates": {
                        "end": "2018-10-28T18:30:00+0000",
                        "start": "2018-10-28T15:00:00+0000",
                        "tz": "Europe/Oslo"
                    },
                    "state": "ingested",
                    "type": "event"
                },
                {
                    "dates": {
                        "end": "2018-11-10T12:00:00+0000",
                        "start": "2018-11-10T11:00:00+0000",
                        "tz": "Europe/Oslo"
                    },
                    "state": "ingested",
                    "type": "event"
                }
            ]
        }
        """
        When we patch "/ingest_providers/#PROVIDER_ID#"
        """
        {
            "private": {
                "search": {
                    "offset": 0
                }
            }
        }
        """
        When we fetch events "0_dates_changed.xml,1.xml,2.xml,3.xml" from "ntb-events-api" NTB Events API provider
        When we get "/events"
        Then we get list with 8 items
        """
        {
            "_items": [
                {
                    "dates": {
                        "end": "2018-09-29T19:25:00+0000",
                        "start": "2018-09-29T16:25:00+0000",
                        "tz": "Europe/Oslo"
                    },
                    "state": "ingested",
                    "type": "event"
                },
                {
                    "dates": {
                        "end": "2018-10-24T18:45:00+0000",
                        "start": "2018-10-24T16:15:00+0000",
                        "tz": "Europe/Oslo"
                    },
                    "state": "ingested",
                    "type": "event"
                },
                {
                    "dates": {
                        "end": "2018-10-26T12:00:00+0000",
                        "start": "2018-10-26T10:30:00+0000",
                        "tz": "Europe/Oslo"
                    },
                    "state": "ingested",
                    "type": "event"
                },
                {
                    "dates": {
                        "end": "2018-10-27T12:00:00+0000",
                        "start": "2018-10-27T10:30:00+0000",
                        "tz": "Europe/Oslo"
                    },
                    "state": "ingested",
                    "type": "event"
                },
                {
                    "dates": {
                        "end": "2018-10-27T16:30:00+0000",
                        "start": "2018-10-27T15:00:00+0000",
                        "tz": "Europe/Oslo"
                    },
                    "state": "ingested",
                    "type": "event"
                },
                {
                    "dates": {
                        "end": "2018-10-28T12:15:00+0000",
                        "start": "2018-10-28T10:45:00+0000",
                        "tz": "Europe/Oslo"
                    },
                    "state": "ingested",
                    "type": "event"
                },
                {
                    "dates": {
                        "end": "2018-10-28T18:30:00+0000",
                        "start": "2018-10-28T15:00:00+0000",
                        "tz": "Europe/Oslo"
                    },
                    "state": "ingested",
                    "type": "event"
                },
                {
                    "dates": {
                        "end": "2018-11-11T12:00:00+0000",
                        "start": "2018-11-11T11:00:00+0000",
                        "tz": "Europe/Oslo"
                    },
                    "state": "ingested",
                    "type": "event"
                }
            ]
        }
        """

    @ntb_vocabulary @auth @ntb_event_api_provider
    Scenario: Ingested event changes status after it was edited
        Given empty "events"
        When we get "/events"
        Then we get list with 0 items
        When we fetch events "0.xml,1.xml,2.xml,3.xml" from "ntb-events-api" NTB Events API provider
        When we get "/events"
        Then we save event id
        When we patch "/events/#EVENT_TO_PATCH#"
        """
        {"dates": {"end": "2019-09-29T19:25:00+0000", "start": "2019-09-29T16:25:00+0000"}}
        """
        Then we get existing resource
        """
        {
           "dates": {
                        "end": "2019-09-29T19:25:00+0000",
                        "start": "2019-09-29T16:25:00+0000",
                        "tz": "Europe/Oslo"
                    },
           "state": "draft",
           "type": "event"
        }
        """

    @ntb_vocabulary @auth @ntb_event_api_provider
    Scenario: Draft events are not updated when feeding service restarted
        Given empty "events"
        When we get "/events"
        Then we get list with 0 items
        When we fetch events "0.xml,1.xml,2.xml,3.xml" from "ntb-events-api" NTB Events API provider
        When we get "/events"
        Then we save event id
        When we patch "/events/#EVENT_TO_PATCH#"
        """
        {"dates": {"end": "2019-09-29T19:25:00+0000", "start": "2019-09-29T16:25:00+0000"}}
        """
        Then we get existing resource
        """
        {
           "dates": {
                        "end": "2019-09-29T19:25:00+0000",
                        "start": "2019-09-29T16:25:00+0000",
                        "tz": "Europe/Oslo"
                    },
           "state": "draft",
           "type": "event"
        }
        """
        When we patch "/ingest_providers/#PROVIDER_ID#"
        """
        {
            "private": {
                "search": {
                    "offset": 0
                }
            }
        }
        """
        When we fetch events "0_dates_changed.xml,1.xml,2.xml,3.xml" from "ntb-events-api" NTB Events API provider
        When we get "/events"
        Then we get list with 8 items
        """
        {
            "_items": [
                {
                    "dates": {
                        "end": "2019-09-29T19:25:00+0000",
                        "start": "2019-09-29T16:25:00+0000",
                        "tz": "Europe/Oslo"
                    },
                    "state": "draft",
                    "type": "event"
                },
                {
                    "dates": {
                        "end": "2018-10-24T18:45:00+0000",
                        "start": "2018-10-24T16:15:00+0000",
                        "tz": "Europe/Oslo"
                    },
                    "state": "ingested",
                    "type": "event"
                },
                {
                    "dates": {
                        "end": "2018-10-26T12:00:00+0000",
                        "start": "2018-10-26T10:30:00+0000",
                        "tz": "Europe/Oslo"
                    },
                    "state": "ingested",
                    "type": "event"
                },
                {
                    "dates": {
                        "end": "2018-10-27T12:00:00+0000",
                        "start": "2018-10-27T10:30:00+0000",
                        "tz": "Europe/Oslo"
                    },
                    "state": "ingested",
                    "type": "event"
                },
                {
                    "dates": {
                        "end": "2018-10-27T16:30:00+0000",
                        "start": "2018-10-27T15:00:00+0000",
                        "tz": "Europe/Oslo"
                    },
                    "state": "ingested",
                    "type": "event"
                },
                {
                    "dates": {
                        "end": "2018-10-28T12:15:00+0000",
                        "start": "2018-10-28T10:45:00+0000",
                        "tz": "Europe/Oslo"
                    },
                    "state": "ingested",
                    "type": "event"
                },
                {
                    "dates": {
                        "end": "2018-10-28T18:30:00+0000",
                        "start": "2018-10-28T15:00:00+0000",
                        "tz": "Europe/Oslo"
                    },
                    "state": "ingested",
                    "type": "event"
                },
                {
                    "dates": {
                        "end": "2018-11-11T12:00:00+0000",
                        "start": "2018-11-11T11:00:00+0000",
                        "tz": "Europe/Oslo"
                    },
                    "state": "ingested",
                    "type": "event"
                }
            ]
        }
        """

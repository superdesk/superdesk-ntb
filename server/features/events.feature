Feature: Events ingest

    @ntb_vocabulary @auth @ntb_event_api_provider
    Scenario: Ingest NTB event API xml
        Given empty "events"
        When we get "/events"
        Then we get list with 0 items
        When we fetch events from "ntb-events-api" NTB Events API provider
        When we get "/events"
        Then we get list with 8 items

    @ntb_vocabulary @auth @ntb_event_api_provider
    Scenario: Ingest NTB event API xml twice
        Given empty "events"
        When we get "/events"
        Then we get list with 0 items
        When we fetch events from "ntb-events-api" NTB Events API provider
        When we fetch events from "ntb-events-api" NTB Events API provider
        When we get "/events"
        Then we get list with 8 items

    @ntb_vocabulary @auth @ntb_event_api_provider
    Scenario: Ingested events list does not contain ntb_id
        Given empty "events"
        When we get "/events"
        Then we get list with 0 items
        When we fetch events from "ntb-events-api" NTB Events API provider
        When we get "/events"
        Then we get list without ntb_id
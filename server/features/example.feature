Feature: Example test

    @auth
    Scenario: Empty ingest providers list
        Given empty "ingest_providers"
        When we get "/ingest_providers"
        Then we get list with 0 items

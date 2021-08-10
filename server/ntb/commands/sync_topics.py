from typing import Optional, Dict, List
from typing_extensions import TypedDict
from os import path
import sys
import json
from datetime import datetime
import requests
import socket
import logging

from flask import current_app as app
import superdesk

logger = logging.getLogger(__name__)
RESOURCE_URL = "https://cv.iptc.org/newscodes/mediatopic"


class CVItem(TypedDict):
    qcode: str
    name: str
    parent: Optional[str]
    iptc_subject: Optional[str]
    wikidata: Optional[str]
    is_active: bool


class VocabJson(TypedDict):
    _id: str
    items: List[CVItem]


VocabFileJson = List[VocabJson]


class CVItemFromIPTC(TypedDict, CVItem):
    _existing: Optional[CVItem]
    _missing_translation: bool


class IPTCTopic(TypedDict):
    qcode: str
    prefLabel: Dict[str, str]
    broader: List[str]
    exactMatch: List[str]
    closeMatch: List[str]


class ReportDeviationData(TypedDict):
    topic: CVItemFromIPTC
    fields: List[str]


class ReportData(TypedDict):
    new: List[CVItemFromIPTC]
    deviated: List[ReportDeviationData]


class SyncTopicsCommand(superdesk.Command):
    """Synchronise MediaTopics CV from IPTC

    Downloads that latest Media Topics json from IPTC server,
    and merges them into the ``data/vocabularies.json`` file.

    A local file can be used instead of downloading from IPTC,
    using the ``--filename`` or ``-f`` argument.

    To allow for a clean commit diff, use ``-t`` or ``--format`` flag
    to standardise the format of the ``data/vocabularies.json`` file first.

    Chore Example:
    ::

        $ python manage.py ntb:sync_topics --format
        $ git commit -a -m "standardise vocabularies.json format"
        $ python manage.py ntb:sync_topics
        $ git add ntb/commands/sync_topics_reports
        $ git commit -a -m "synchronise Media Topics from IPTC"

    Command Examples:
    ::

        $ python manage.py ntb:sync_topics
        $ python manage.py ntb:sync_topics --file /tmp/iptc-media-topcs.json
        $ python manage.py ntb:sync_topics --format
        $ python manage.py ntb:sync_topics --output /tmp/vocabularies.json
        $ python manage.py ntb:sync_topics --format --output /tmp/vocabularies.json
    """

    option_list = [
        superdesk.Option(
            "--file",
            "-f",
            dest="filename",
            required=False,
            help="Use a local json file to sync topics from",
        ),
        superdesk.Option(
            "--format",
            "-t",
            dest="format_json",
            action="store_true",
            required=False,
            help="Standardise the format of the vocabularies.json file"
        ),
        superdesk.Option(
            "--output",
            "-o",
            dest="output",
            required=False,
            help="Changes the output file where changes are written. Useful for development."
        )
    ]

    def run(self, filename: Optional[str] = None, output: Optional[str] = None, format_json: bool = False):
        if format_json:
            self._run_standardise_vocabs(output)
        else:
            self._run_synchronise_vocabs(filename, output)

    def _run_standardise_vocabs(self, output: Optional[str] = None):
        """Standardise the JSON format of the vocabularies.json file

        This allows for a clean diff after synchronising the Media Topics
        as ``json.dumps`` may differ from human created changes.
        """

        logger.info("Standardising the format of vocabularies.json file (skipping sync)")

        vocabularies_json = self._load_vocabularies_json()
        self._format_json(vocabularies_json, output)

    def _run_synchronise_vocabs(self, filename: Optional[str] = None, output: Optional[str] = None):
        """Synchronise the Media Topics vocab from IPTC"""

        logger.info("Starting to synchronise Media Topics")
        vocabularies_json = self._load_vocabularies_json()

        existing_topics = self._get_existing_topics_from_cv(vocabularies_json)
        updated_topics = self._get_updated_topics_from_iptc(filename)
        report = self._generate_report_data(updated_topics, existing_topics)
        self._generate_report(report, updated_topics)
        self._update_vocabularies_json(vocabularies_json, updated_topics)
        self._write_changes_to_vocabularies_json(vocabularies_json, output)

    def _get_vocabularies_json_path(self) -> str:
        return path.join(app.config["ABS_PATH"], "data", "vocabularies.json")

    def _load_vocabularies_json(self) -> VocabFileJson:
        """Loads the MediaTopics json from the local filesystem"""

        try:
            with open(self._get_vocabularies_json_path(), "rb") as f:
                return json.load(f)
        except IOError:
            logger.exception("Failed to load vocabularies.json file")
            sys.exit(1)

    def _format_json(self, vocabularies_json: VocabFileJson, output: Optional[str] = None):
        """Write the json data back to the vocabularies.json file"""

        try:
            file_path = output or self._get_vocabularies_json_path()
            with open(file_path, "w") as f:
                f.write(
                    json.dumps(
                        vocabularies_json,
                        ensure_ascii=False,
                        indent=4
                    )
                )
                f.write("\r\n")
        except IOError:
            logger.exception("Failed to write changes to vocabularies.json file")
            sys.exit(1)

    def _get_existing_topics_from_cv(self, vocabularies_json: VocabFileJson) -> Dict[str, CVItem]:
        """Returns dictionary of MediaTopics from vocabularies.json"""

        for vocab in vocabularies_json:
            if vocab.get("_id") == "topics":
                return {
                    topic["qcode"]: topic
                    for topic in vocab.get("items") or []
                }

        return {}

    def _get_updated_topics_from_iptc(self, filename: Optional[str] = None) -> List[CVItemFromIPTC]:
        """Get MediaTopics in CV format from IPTC format"""

        return [
            self._convert_iptc_to_cv(item)
            for item in self._download_topics_json(filename)
        ]

    def _download_topics_json(self, filename: Optional[str] = None) -> List[IPTCTopic]:
        """Downloads the MediaTopics json file

        Requests all languages as not all entries contain Norwegian translation.
        Uses a local file instead if ``filename`` is defined
        """

        try:
            if filename:
                with open(filename, "rb") as f:
                    data = json.load(f)
            else:
                r = requests.get(RESOURCE_URL, params={"lang": "x-all", "format": "json"})
                data = r.json()
        except (socket.gaierror, json.JSONDecodeError, IOError):
            logger.exception("Failed to load IPTC Media Topics")
            sys.exit(1)

        return data.get("conceptSet") or []

    def _convert_iptc_to_cv(self, entry: IPTCTopic) -> CVItemFromIPTC:
        """Convert IPTC item to Superdesk CV format"""

        entry.setdefault("prefLabel", {})
        entry.setdefault("broader", [])
        entry.setdefault("exactMatch", [])
        entry.setdefault("closeMatch", [])

        def get_name() -> str:
            return entry["prefLabel"].get("no") or \
                entry["prefLabel"].get("en") or \
                entry["prefLabel"].get("en-US") or \
                entry["prefLabel"].get("en-GB") or ""

        def get_parent() -> Optional[str]:
            try:
                return extract_code_from_string(entry["broader"][0])
            except IndexError:
                return None

        def extract_code_from_string(value) -> Optional[str]:
            try:
                return value.rsplit("/", 1)[1]
            except (IndexError, ValueError):
                return None

        def get_closest_match(search_string) -> Optional[str]:
            for match_type in ["exactMatch", "closeMatch"]:
                for match in entry[match_type]:  # type: ignore
                    if search_string in match:
                        return extract_code_from_string(match)

            return None

        return CVItemFromIPTC(
            qcode=entry["qcode"][7:],  # remove ``medtop:`` from the qcode
            name=get_name(),
            parent=get_parent(),
            iptc_subject=get_closest_match("subjectcode"),
            wikidata=get_closest_match("wikidata"),
            is_active=True,
            _existing=None,
            _missing_translation=not entry["prefLabel"].get("no")
        )

    def _generate_report_data(
        self,
        updated_topics: List[CVItemFromIPTC],
        existing_topics: Dict[str, CVItem]
    ) -> ReportData:
        """Generate data for reporting the changes to the local Media Topics CV

        ``report["new"]``: New items from IPTC that aren't in local CV
        ``report["deviated"]``: List of items where attribute values have deviated from IPTC
        """

        report = ReportData(
            new=[],
            deviated=[]
        )

        for topic in updated_topics:
            original = existing_topics.get(topic["qcode"])
            topic["_existing"] = original

            if not original:
                # This is a new Media Topic, add it to the report
                report["new"].append(topic)
                continue
            elif not original.get("is_active"):
                # Skip this Media Topic, as it is disabled in local CV
                continue

            deviations = []

            for field in ["name", "parent", "wikidata", "iptc_subject"]:
                # Ignore types here, otherwise the mypy fails with
                # TypedDict key must be a string literal
                if (
                    len(original.get(field) or "") and  # type: ignore
                    len(topic.get(field) or "") and  # type: ignore
                    topic[field] != original[field]  # type: ignore
                ):
                    # This field exists in both local CV and IPTC
                    # but the values differ. Add this to list of deviated fields
                    deviations.append(field)

            if len(deviations):
                # The local Media Topic has deviated from IPTC
                # Add this to the report
                report["deviated"].append({
                    "topic": topic,
                    "fields": deviations,
                })

        return report

    def _generate_report(self, report: ReportData, topics: List[CVItemFromIPTC]):
        """Generate and write the report to a markdown file

        Writes the file to ``server/ntb/commands/sync_topics_reports``
        The report uses markdown and table to show the data.
        """

        output: List[str] = []
        self._gen_new_table(report["new"], output)
        self._gen_translation_table(topics, output)
        self._gen_deviated_table(report["deviated"], output)

        file_path = path.abspath(
            path.join(
                path.dirname(__file__),
                "sync_topics_reports",
                f"{datetime.now():%Y-%m-%dT%H-%M}.md"
            )
        )

        with open(file_path, "w") as f:
            f.write('\r\n'.join(output))

    def _gen_new_table(self, topics: List[CVItemFromIPTC], output: List[str]):
        """Generate markdown table for newly added IPTC Media Topics"""

        output.extend([
            "",
            "New Items:",
            "",
            "| Qcode | Name | Parent | Wikidata | IPTC Subject |",
            "| ----- | ---- | ------ | -------- | ------------ |",
        ])

        for topic in topics:
            qcode = topic.get("qcode") or ""
            name = topic.get("name") or ""
            parent = topic.get("parent") or ""
            wikidata = topic.get("wikidata") or ""
            iptc_subject = topic.get("iptc_subject") or ""
            output.append(f"| {qcode} | {name} | {parent} | {wikidata} | {iptc_subject} |")

    def _gen_translation_table(self, topics: List[CVItemFromIPTC], output: List[str]):
        """Generate markdown table for IPTC Media Topics without Norwegian translations"""

        output.extend([
            "",
            "Missing Norwegian Translation:",
            "",
            "| Qcode | Name |",
            "| ----- | ---- |",
        ])

        for topic in topics:
            if topic["_missing_translation"]:
                qcode = topic.get("qcode") or ""
                name = topic.get("name") or ""
                output.append(f"| {qcode} | {name} |")

    def _gen_deviated_table(self, items: List[ReportDeviationData], output: List[str]):
        """Generate markdown table items that have deviated from IPTC Media Topics"""

        output.extend([
            "",
            "Deviated Items:",
            "",
            "| Qcode | Field | Existing | IPTC |",
            "| ----- | ----- | -------- | ---- |",
        ])

        for item in items:
            topic = item["topic"]
            qcode = topic.get("qcode")
            fields = item.get("fields") or []
            existing = topic.get("_existing")
            for field in fields:
                existing_value = existing.get(field, "") if existing else ""
                iptc_value = topic.get(field) or ""
                output.append(f"| {qcode} | {field} | {existing_value} | {iptc_value} |")

    def _update_vocabularies_json(self, vocabularies_json: VocabFileJson, updated_topics: List[CVItemFromIPTC]):
        """Updates the vocabularies json data with the synchronised Media Topics"""

        # Map the IPTC Media Topics by ``qcode`` for easier retrieval by qcode
        updated_topics_by_id = {
            topic["qcode"]: topic
            for topic in updated_topics
        }

        for vocab in vocabularies_json:
            if vocab.get("_id") != "topics":
                # We only want to update the ``topics`` CV
                # skip this entry
                continue

            vocab.setdefault("items", [])

            # Update existing local CV items
            for item in vocab["items"]:
                iptc_item = updated_topics_by_id[item["qcode"]]

                for field in ["name", "parent", "iptc_subject", "wikidata"]:
                    # Only apply values to fields that are not defined in local CV
                    # Deviations from IPTC should be submitted manually from the report
                    item[field] = item.get(field) or iptc_item.get(field)  # type: ignore

            # Add new Media Topics to the local CV
            # default to being enabled
            for qcode, item in updated_topics_by_id.items():
                if not item["_existing"]:
                    vocab["items"].append({
                        "qcode": item["qcode"],
                        "name": item["name"],
                        "parent": item["parent"],
                        "iptc_subject": item["iptc_subject"],
                        "wikidata": item["wikidata"],
                        "is_active": True
                    })

    def _write_changes_to_vocabularies_json(
        self,
        vocabularies_json: VocabFileJson,
        output: Optional[str] = None
    ):
        """Writes the updated vocabularies json to file"""

        try:
            file_path = output or self._get_vocabularies_json_path()
            with open(file_path, "w") as f:
                f.write(
                    json.dumps(
                        vocabularies_json,
                        ensure_ascii=False,
                        indent=4
                    )
                )
                f.write("\r\n")
        except IOError:
            logger.exception("Failed to update vocabularies.json file")
            sys.exit(1)

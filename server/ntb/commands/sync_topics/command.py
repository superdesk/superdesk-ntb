from typing import Optional, Dict, List
from os import path
import sys
import json
import logging

from flask import current_app as app
import superdesk

from .common import CVItem, VocabFileJson, CVItemFromIPTC
from .iptc_json import get_cv_items_from_iptc_json
from .iptc_xlsx import get_cv_items_from_iptc_xlsx
from .report import generate_topics_report

logger = logging.getLogger(__name__)
RESOURCE_URL = "https://cv.iptc.org/newscodes/mediatopic"


class SyncTopicsCommand(superdesk.Command):
    """Synchronise MediaTopics CV from IPTC

    Downloads that latest Media Topics json from IPTC server,
    and merges them into the ``data/vocabularies.json`` file.

    A local file can be used instead of downloading from IPTC,
    using the ``--filename`` or ``-f`` argument.

    ``source-format`` or ``-s`` can be used to control the format of the file.
    Supported format types are JSON (``-s json``) or XLSX (``-s xlsx``).

    To allow for a clean commit diff, use ``-t`` or ``--format`` flag
    to standardise the format of the ``data/vocabularies.json`` file first.

    By default, values of existing items won't be overridden by the supplied file,
    unless the value is not defined. You can force to use the supplied file instead
    for certain fields using the ``--override`` value with a comma separated list of values.
    Available fields are ``name``, ``parent``, ``iptc_subject`` and/or ``wikidata``.

    Override Example:
    ::

        $ python manage.py ntb:sync_topics --override "_all"
        $ python manage.py ntb:sync_topics --override "name"
        $ python manage.py ntb:sync_topics --override "name,iptc_subject"

    Chore Example:
    ::

        $ python manage.py ntb:sync_topics --format
        $ git commit -a -m "standardise vocabularies.json format"
        $ python manage.py ntb:sync_topics
        $ git add ntb/commands/sync_topics_reports
        $ git commit -a -m "synchronise Media Topics from IPTC"

    Chore Example (using provided xlsx file, overriding ``name`` only)
    ::

        $ python manage.py ntb:sync_topics --format
        $ git commit -a -m "standardise vocabularies.json format"
        $ python manage.py ntb:sync_topics --file IPTC-MediaTopic-NewsCodes.xlsx --source-format xlsx --override "name"
        $ git add ntb/commands/sync_topics_reports
        $ git commit -a -m "synchronise Media Topics from IPTC"

    Command Examples:
    ::

        $ python manage.py ntb:sync_topics
        $ python manage.py ntb:sync_topics --file /tmp/iptc-media-topcs.json
        $ python manage.py ntb:sync_topics --format
        $ python manage.py ntb:sync_topics --output /tmp/vocabularies.json
        $ python manage.py ntb:sync_topics --format --output /tmp/vocabularies.json
        $ python manage.py ntb:sync_topics --override "name,iptc_subject"
        $ python manage.py ntb:sync_topics --override "_all"
        $ python manage.py ntb:sync_topics --file IPTC-MediaTopic-NewsCodes.xlsx --source-format xlsx
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
        ),
        superdesk.Option(
            "--source-format",
            "-s",
            dest="source_format",
            required=False,
            default="json",
            choices=["json", "xlsx"],
            help="Specify the format of the local file (JSON or XLSX Spreadsheet)"
        ),
        superdesk.Option(
            "--override",
            "-r",
            dest="override_fields",
            required=False,
            help="Specify the fields to override (if a value already exists), as a comma separated list. "
                 "Use `--override _all` to override all values"
        )
    ]

    def run(
        self,
        filename: Optional[str] = None,
        output: Optional[str] = None,
        format_json: bool = False,
        source_format: str = "json",
        override_fields: Optional[str] = None,
    ):
        if format_json:
            self._run_standardise_vocabs(output)
        else:
            self._run_synchronise_vocabs(filename, output, source_format, override_fields)

    def _run_standardise_vocabs(self, output: Optional[str] = None):
        """Standardise the JSON format of the vocabularies.json file

        This allows for a clean diff after synchronising the Media Topics
        as ``json.dumps`` may differ from human created changes.
        """

        logger.info("Standardising the format of vocabularies.json file (skipping sync)")

        vocabularies_json = self._load_vocabularies_json()
        self._format_json(vocabularies_json, output)

    def _run_synchronise_vocabs(
        self,
        filename: Optional[str] = None,
        output: Optional[str] = None,
        source_format: str = "json",
        override_fields: Optional[str] = None
    ):
        """Synchronise the Media Topics vocab from IPTC"""

        logger.info("Starting to synchronise Media Topics")

        # Load existing and updated MediaTopics
        vocabularies_json = self._load_vocabularies_json()
        existing_topics = self._get_existing_topics_from_cv(vocabularies_json)
        updated_topics = self._get_updated_topics_from_iptc(existing_topics, filename, source_format)

        self._update_vocabularies_json(vocabularies_json, updated_topics, override_fields)
        generate_topics_report(updated_topics)
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

    def _get_updated_topics_from_iptc(
        self,
        existing_topics: Dict[str, CVItem],
        filename: Optional[str] = None,
        source_format: str = "json"
    ) -> List[CVItemFromIPTC]:
        """Get MediaTopics in CV format from IPTC format"""

        if source_format == "xlsx":
            if not filename:
                logger.error("`--filename` required when `--source-format` is `xlsx`")
                sys.exit(1)
            return get_cv_items_from_iptc_xlsx(existing_topics, filename)
        else:
            return get_cv_items_from_iptc_json(existing_topics, filename)

    def _update_vocabularies_json(
        self,
        vocabularies_json: VocabFileJson,
        updated_topics: List[CVItemFromIPTC],
        override_fields: Optional[str] = None
    ):
        """Updates the vocabularies json data with the synchronised Media Topics"""

        # Map the IPTC Media Topics by ``qcode`` for easier retrieval by qcode
        updated_topics_by_id = {
            topic["qcode"]: topic
            for topic in updated_topics
        }

        if override_fields == "_all":
            override_fields = "name,parent,iptc_subject,wikidata"
        override_fields_list = override_fields.split(",") if override_fields else []

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

                    if field in override_fields_list:
                        item[field] = iptc_item.get(field) or item.get(field)  # type: ignore
                    else:
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

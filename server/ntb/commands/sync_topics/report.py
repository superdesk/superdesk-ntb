from typing import List
from typing_extensions import TypedDict
from os import path
from datetime import datetime

from .common import CVItemFromIPTC


class ReportDeviationData(TypedDict):
    topic: CVItemFromIPTC
    fields: List[str]


class ReportData(TypedDict):
    new: List[CVItemFromIPTC]
    deviated: List[ReportDeviationData]


def generate_topics_report(updated_topics: List[CVItemFromIPTC]):
    report = _generate_report_data(updated_topics)
    _generate_report(report, updated_topics)


def _generate_report_data(updated_topics: List[CVItemFromIPTC]) -> ReportData:
    """Generate data for reporting the changes to the local Media Topics CV

    ``report["new"]``: New items from IPTC that aren't in local CV
    ``report["deviated"]``: List of items where attribute values have deviated from IPTC
    """

    report = ReportData(
        new=[],
        deviated=[]
    )

    for topic in updated_topics:
        original = topic["_existing"]

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


def _generate_report(report: ReportData, topics: List[CVItemFromIPTC]):
    """Generate and write the report to a markdown file

    Writes the file to ``server/ntb/commands/sync_topics_reports``
    The report uses markdown and table to show the data.
    """

    output: List[str] = []
    _gen_new_table(report["new"], output)
    _gen_translation_table(topics, output)
    _gen_deviated_table(report["deviated"], output)

    file_path = path.abspath(
        path.join(
            path.dirname(__file__),
            "../sync_topics_reports",
            f"{datetime.now():%Y-%m-%dT%H-%M}.md"
        )
    )

    with open(file_path, "w") as f:
        f.write('\r\n'.join(output))


def _gen_new_table(topics: List[CVItemFromIPTC], output: List[str]):
    """Generate markdown table for newly added IPTC Media Topics"""

    output.extend([
        "",
        "New Items:",
        "----------",
    ])

    if not len(topics):
        output.append("No new items discovered")
        return

    output.extend([
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


def _gen_translation_table(topics: List[CVItemFromIPTC], output: List[str]):
    """Generate markdown table for IPTC Media Topics without Norwegian translations"""

    output.extend([
        "",
        "Missing Norwegian Translation:",
        "------------------------------",
    ])

    missing_translations = [
        topic
        for topic in topics
        if topic["_missing_translation"]
    ]

    if not len(missing_translations):
        output.append("All Topics are translated")
        return

    output.extend([
        "",
        "| Qcode | Name |",
        "| ----- | ---- |",
    ])

    for topic in missing_translations:
        qcode = topic.get("qcode") or ""
        name = topic.get("name") or ""
        output.append(f"| {qcode} | {name} |")


def _gen_deviated_table(items: List[ReportDeviationData], output: List[str]):
    """Generate markdown table items that have deviated from IPTC Media Topics"""

    output.extend([
        "",
        "Deviated Items:",
        "---------------",
    ])

    if not len(items):
        output.append("Not deviated items found")
        return

    output.extend([
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

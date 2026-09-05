#!/usr/bin/env python3
"""
Sync BACKLOG.md (Sketched ideas) and projects/*.md (status: planned) into
the shared Notion Projects database.

Full reconciliation on every run: reads the current state of both files,
compares it against every Notion row this sync owns (Status = Sketched or
Planned), and:
  - creates a Notion row for any current Sketched/Planned title that
    doesn't have one yet
  - updates the Status/description/date on rows that already exist
  - marks a row Dropped if its title is no longer in BACKLOG.md or in a
    Planned projects/*.md file -- UNLESS that title still appears
    somewhere in STATE.md, which is the safety net for an idea that
    graduated straight past the pointer-file stage (some active projects,
    like an n8n-only workflow, never get a projects/*.md file at all).
    A false "Dropped" is worse than a stale label, so this only drops
    a title that is missing everywhere.

Never touches rows whose current Notion Status is Active, Paused, Done,
or already Dropped -- those belong to the per-project hooks and to
Matt's own STATE.md edits, not to this script.

Depends on a convention this sync requires going forward: when an idea
graduates from BACKLOG.md to a projects/*.md pointer file, the pointer
file's `name` field must reuse the BACKLOG.md heading text exactly. That
is how the same Notion row is found and updated in place instead of the
old one silently going stale while a new one gets created.
"""
import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.request

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "")
NOTION_VERSION = "2022-06-28"

MANAGED_STATUSES = {"Sketched", "Planned"}
MAX_TEXT = 500


def notion_request(method, path, body=None):
    url = f"https://api.notion.com/v1{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {NOTION_TOKEN}")
    req.add_header("Notion-Version", NOTION_VERSION)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        print(f"::error::Notion API {method} {path} failed ({e.code}): {body_text}")
        raise


def parse_backlog(path):
    """Returns {title: description} for every '## ' heading in BACKLOG.md."""
    if not os.path.exists(path):
        return {}
    text = open(path, encoding="utf-8").read()
    items = {}
    parts = re.split(r"^##[ \t]+(.+)$", text, flags=re.MULTILINE)
    # parts[0] is the preamble before the first heading; after that the
    # list alternates (title, body-until-next-heading).
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        body = parts[i + 1].strip() if i + 1 < len(parts) else ""
        items[title] = body
    return items


def parse_frontmatter(text):
    """Small parser for the fixed pointer-file shape:
        ---
        key: "value"
        ---
        description text
    Returns (fields_dict, description_text).
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, text.strip()
    fields = {}
    i = 1
    while i < len(lines) and lines[i].strip() != "---":
        line = lines[i]
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            # Strip a matching pair of surrounding quotes, not every quote.
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            fields[key] = value
        i += 1
    description = "\n".join(lines[i + 1:]).strip()
    return fields, description


def parse_planned_projects(dir_path):
    """Returns {title: description} for every projects/*.md file whose
    frontmatter status is 'planned'. Title is the frontmatter 'name'
    field verbatim."""
    items = {}
    if not os.path.isdir(dir_path):
        return items
    for fname in sorted(os.listdir(dir_path)):
        if not fname.endswith(".md") or fname == "_TEMPLATE.md":
            continue
        text = open(os.path.join(dir_path, fname), encoding="utf-8").read()
        fields, description = parse_frontmatter(text)
        if fields.get("status", "").lower() == "planned":
            title = fields.get("name", "").strip()
            if title:
                items[title] = description
    return items


def fetch_all_rows():
    """Returns {title: {"id": page_id, "status": status_name_or_None}}
    for every row currently in the database."""
    rows = {}
    body = {"page_size": 100}
    while True:
        _, result = notion_request(
            "POST", f"/databases/{NOTION_DATABASE_ID}/query", body
        )
        for page in result.get("results", []):
            props = page["properties"]
            title_prop = props.get("Project", {}).get("title", [])
            title = "".join(t.get("plain_text", "") for t in title_prop).strip()
            status_prop = props.get("Status", {}).get("select")
            status_name = status_prop["name"] if status_prop else None
            if title:
                rows[title] = {"id": page["id"], "status": status_name}
        if result.get("has_more"):
            body["start_cursor"] = result["next_cursor"]
        else:
            break
    return rows


def upsert(existing_rows, title, status_name, description, today):
    props = {
        "Status": {"select": {"name": status_name}},
        "Last Updated": {"date": {"start": today}},
        "Latest Update": {
            "rich_text": [{"text": {"content": description[:MAX_TEXT]}}]
        },
        "Source": {"select": {"name": "GitHub Hook"}},
    }
    if title in existing_rows:
        page_id = existing_rows[title]["id"]
        notion_request("PATCH", f"/pages/{page_id}", {"properties": props})
        print(f"updated: {title} -> {status_name}")
    else:
        props["Project"] = {"title": [{"text": {"content": title}}]}
        notion_request(
            "POST",
            "/pages",
            {"parent": {"database_id": NOTION_DATABASE_ID}, "properties": props},
        )
        print(f"created: {title} -> {status_name}")


def mark_dropped(page_id, title, today):
    notion_request(
        "PATCH",
        f"/pages/{page_id}",
        {
            "properties": {
                "Status": {"select": {"name": "Dropped"}},
                "Last Updated": {"date": {"start": today}},
            }
        },
    )
    print(f"dropped: {title}")


def main():
    if not NOTION_TOKEN or not NOTION_DATABASE_ID:
        print("::error::NOTION_TOKEN and/or NOTION_DATABASE_ID repo secrets are not set.")
        sys.exit(1)

    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

    sketched = parse_backlog("BACKLOG.md")
    planned = parse_planned_projects("projects")
    state_text = (
        open("STATE.md", encoding="utf-8").read() if os.path.exists("STATE.md") else ""
    )

    current_titles = set(sketched) | set(planned)
    overlap = set(sketched) & set(planned)
    if overlap:
        print(
            f"::warning::Title(s) in both BACKLOG.md and a Planned pointer file at "
            f"once -- CLAUDE.md says that shouldn't happen: {sorted(overlap)}"
        )

    existing_rows = fetch_all_rows()

    dropped = 0
    for title, info in existing_rows.items():
        if info["status"] not in MANAGED_STATUSES:
            continue
        if title in current_titles:
            continue
        if title in state_text:
            print(f"skipped drop (still mentioned in STATE.md): {title}")
            continue
        mark_dropped(info["id"], title, today)
        dropped += 1

    for title, description in sketched.items():
        upsert(existing_rows, title, "Sketched", description, today)
    for title, description in planned.items():
        upsert(existing_rows, title, "Planned", description, today)

    print(
        f"Sync complete: {len(sketched)} sketched, {len(planned)} planned, "
        f"{dropped} dropped."
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 - top-level safety net for CI logs
        print(f"::error::notion_backlog_sync.py failed: {exc}")
        sys.exit(1)

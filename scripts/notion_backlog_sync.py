#!/usr/bin/env python3
"""
Sync BACKLOG.md (Sketched ideas) and projects/*.md (every status) into the
shared Notion Projects database.

Two different jobs, split by which fields each one is allowed to touch:

1. Sketched (BACKLOG.md) and Planned (projects/*.md with status: planned) --
   this script fully owns these rows. Full reconciliation on every run:
   reads the current state of both sources, compares it against every
   Notion row this sync owns (Status = Sketched or Planned), and:
     - creates a Notion row for any current Sketched/Planned title that
       doesn't have one yet (Description + Status + a "Added to roadmap
       on <date>" Latest Update)
     - moves a row's Status if the title's status changed on disk (e.g.
       Sketched -> Planned), stamping Latest Update as "Moved to <status>
       on <date>" -- but leaves Latest Update (and Last Updated) alone
       when nothing actually changed, so "latest" stays true instead of
       bumping to today on every unrelated push
     - marks a row Dropped if its title is no longer in BACKLOG.md or in
       a Planned projects/*.md file -- UNLESS that title still appears
       somewhere in STATE.md, which is the safety net for an idea that
       graduated straight past the pointer-file stage (some active
       projects, like an n8n-only workflow, never get a projects/*.md
       file at all). A false "Dropped" is worse than a stale label, so
       this only drops a title that is missing everywhere.

2. Every other projects/*.md file (status: active | paused | done) --
   this script only ever seeds that row's Description, and only if it's
   currently blank. Status, Last Updated, Latest Update, and Source for
   those rows belong to that project's own per-repo GitHub Actions hook
   (or to Matt's own manual STATE.md-driven fixes) -- this script never
   touches them.

Description itself is seed-once, hands-off, for every row regardless of
which job created it: written once when a Notion row's Description is
still blank, then left alone for good so Matt can polish the wording
directly in Notion without a later disk edit clobbering it. Keep
BACKLOG.md entries and pointer-file bodies to one or two plain-language
sentences -- that text becomes this column verbatim the first time a row
is created or first synced.

Never touches Status/Last Updated/Latest Update/Source on rows whose
current Notion Status is Active, Paused, Done, or already Dropped --
those belong to the per-project hooks and to Matt's own STATE.md edits,
not to this script.

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
UNMANAGED_STATUSES = {"active", "paused", "done"}
MAX_TEXT = 500


def today_human(dt=None):
    """'September 6, 2026' -- full month name, no leading zero on the day."""
    dt = dt or datetime.datetime.now(datetime.timezone.utc)
    return f"{dt.strftime('%B')} {dt.day}, {dt.year}"


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


def parse_all_pointer_files(dir_path):
    """Returns {title: {"status": status_lower, "description": text}} for
    every projects/*.md file, regardless of status. Title is the
    frontmatter 'name' field verbatim."""
    items = {}
    if not os.path.isdir(dir_path):
        return items
    for fname in sorted(os.listdir(dir_path)):
        if not fname.endswith(".md") or fname == "_TEMPLATE.md":
            continue
        text = open(os.path.join(dir_path, fname), encoding="utf-8").read()
        fields, description = parse_frontmatter(text)
        title = fields.get("name", "").strip()
        status = fields.get("status", "").strip().lower()
        if title:
            items[title] = {"status": status, "description": description}
    return items


def fetch_all_rows():
    """Returns {title: {"id": page_id, "status": status_name_or_None,
    "description": current_description_text}} for every row currently in
    the database."""
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
            desc_prop = props.get("Description", {}).get("rich_text", [])
            description = "".join(t.get("plain_text", "") for t in desc_prop).strip()
            if title:
                rows[title] = {
                    "id": page["id"],
                    "status": status_name,
                    "description": description,
                }
        if result.get("has_more"):
            body["start_cursor"] = result["next_cursor"]
        else:
            break
    return rows


def upsert_managed(existing_rows, title, status_name, description, today):
    """Full owner of Sketched/Planned rows: creates, moves status, seeds
    Description once. Leaves everything alone when nothing changed."""
    if title not in existing_rows:
        props = {
            "Project": {"title": [{"text": {"content": title}}]},
            "Status": {"select": {"name": status_name}},
            "Last Updated": {"date": {"start": today}},
            "Latest Update": {
                "rich_text": [{"text": {"content": f"Added to roadmap on {today_human()}."}}]
            },
            "Source": {"select": {"name": "GitHub Hook"}},
            "Description": {
                "rich_text": [{"text": {"content": description[:MAX_TEXT]}}]
            },
        }
        notion_request(
            "POST",
            "/pages",
            {"parent": {"database_id": NOTION_DATABASE_ID}, "properties": props},
        )
        print(f"created: {title} -> {status_name}")
        return

    row = existing_rows[title]
    props = {}
    if row["status"] != status_name:
        props["Status"] = {"select": {"name": status_name}}
        props["Last Updated"] = {"date": {"start": today}}
        props["Latest Update"] = {
            "rich_text": [{"text": {"content": f"Moved to {status_name} on {today_human()}."}}]
        }
    if not row["description"]:
        props["Description"] = {
            "rich_text": [{"text": {"content": description[:MAX_TEXT]}}]
        }
    if not props:
        print(f"unchanged: {title}")
        return
    notion_request("PATCH", f"/pages/{row['id']}", {"properties": props})
    print(f"updated: {title} -> {status_name} ({', '.join(props)})")


def seed_description_only(existing_rows, title, description):
    """For active/paused/done pointer files: never touches Status, dates,
    or Source. Only fills Description, and only if currently blank."""
    row = existing_rows.get(title)
    if not row:
        # No Notion row yet for this project -- that row gets created by
        # the per-project hook or a manual seed, not by this script.
        return
    if row["description"]:
        return
    if not description:
        return
    notion_request(
        "PATCH",
        f"/pages/{row['id']}",
        {"properties": {"Description": {"rich_text": [{"text": {"content": description[:MAX_TEXT]}}]}}},
    )
    print(f"seeded description only: {title}")


def mark_dropped(page_id, title, today):
    notion_request(
        "PATCH",
        f"/pages/{page_id}",
        {
            "properties": {
                "Status": {"select": {"name": "Dropped"}},
                "Last Updated": {"date": {"start": today}},
                "Latest Update": {
                    "rich_text": [{"text": {"content": f"Dropped from roadmap on {today_human()}."}}]
                },
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
    all_pointers = parse_all_pointer_files("projects")
    planned = {t: v["description"] for t, v in all_pointers.items() if v["status"] == "planned"}
    unmanaged = {
        t: v["description"] for t, v in all_pointers.items() if v["status"] in UNMANAGED_STATUSES
    }
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
        existing_rows[title]["status"] = "Dropped"  # keep local view consistent

    for title, description in sketched.items():
        upsert_managed(existing_rows, title, "Sketched", description, today)
    for title, description in planned.items():
        upsert_managed(existing_rows, title, "Planned", description, today)

    for title, description in unmanaged.items():
        seed_description_only(existing_rows, title, description)

    print(
        f"Sync complete: {len(sketched)} sketched, {len(planned)} planned, "
        f"{len(unmanaged)} active/paused/done pointer files checked for description, "
        f"{dropped} dropped."
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 - top-level safety net for CI logs
        print(f"::error::notion_backlog_sync.py failed: {exc}")
        sys.exit(1)

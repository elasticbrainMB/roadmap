#!/usr/bin/env python3
"""
One-off manual cleanup, 2026-09-06. Run once via the paired
`.github/workflows/notion-manual-fix-2026-09-06.yml` workflow_dispatch
trigger, not part of the regular sync.

Two fixes, each guarded by an assertion on the exact shape expected --
if the database doesn't look like what this script was written for, it
aborts loudly and changes nothing, rather than guessing:

1. "infra-watch" has two rows in Notion (a stale Planned one left over
   from before it went Active, plus the real Active one). Archives the
   Planned duplicate. The regular sync never cleans this up itself,
   because its own safety net (skip dropping a title still mentioned in
   STATE.md) was written for a different case -- a project's title is
   *always* still in STATE.md once it's Active, so a stale Planned
   duplicate from a graduated project is invisible to that check.

2. "Cycling-day rating" (an n8n-only workflow with no projects/*.md
   pointer file, so the regular sync never touches its row at all) is
   done, per Matt. Sets its Status to Done.

Both fixes re-fetch the affected page(s) after writing and assert the
change actually stuck before declaring success.
"""
import datetime
import json
import os
import sys
import urllib.error
import urllib.request

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "")
NOTION_VERSION = "2022-06-28"


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


def fetch_all_rows():
    """Returns a list of {"id", "title", "status", "archived"} for every
    row currently in the database (including already-archived ones, since
    the query API excludes archived pages by default -- we want to see
    everything so a re-run of this script is safely idempotent)."""
    rows = []
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
            rows.append({
                "id": page["id"],
                "title": title,
                "status": status_name,
                "archived": page.get("archived", False),
            })
        if result.get("has_more"):
            body["start_cursor"] = result["next_cursor"]
        else:
            break
    return rows


def main():
    if not NOTION_TOKEN or not NOTION_DATABASE_ID:
        print("::error::NOTION_TOKEN and/or NOTION_DATABASE_ID repo secrets are not set.")
        sys.exit(1)

    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

    rows = fetch_all_rows()
    print(f"Fetched {len(rows)} row(s) from the database:")
    for r in rows:
        print(f"  - {r['title']!r} | status={r['status']} | archived={r['archived']}")

    # --- Fix 1: infra-watch duplicate ---
    infra_rows = [r for r in rows if r["title"].strip().lower() == "infra-watch" and not r["archived"]]
    if len(infra_rows) != 2:
        sys.exit(
            f"ABORT (fix 1): expected exactly 2 non-archived 'infra-watch' rows, "
            f"found {len(infra_rows)}: {infra_rows}"
        )
    planned = [r for r in infra_rows if (r["status"] or "").strip().lower() == "planned"]
    active = [r for r in infra_rows if (r["status"] or "").strip().lower() == "active"]
    if len(planned) != 1 or len(active) != 1:
        sys.exit(
            f"ABORT (fix 1): expected one Planned + one Active 'infra-watch' row, "
            f"found statuses {[r['status'] for r in infra_rows]}"
        )
    dupe = planned[0]
    print(f"Fix 1: archiving duplicate infra-watch row {dupe['id']} (status was Planned)")
    notion_request("PATCH", f"/pages/{dupe['id']}", {"archived": True})
    _, check = notion_request("GET", f"/pages/{dupe['id']}")
    if not check.get("archived"):
        sys.exit(f"ABORT (fix 1): archived the page but re-fetch shows archived={check.get('archived')}")
    print("Fix 1: confirmed -- duplicate infra-watch Planned row is archived. Active row untouched.")

    # --- Fix 2: Cycling-day rating -> Done ---
    cycling_rows = [r for r in rows if "cycl" in r["title"].strip().lower() and not r["archived"]]
    if len(cycling_rows) != 1:
        sys.exit(
            f"ABORT (fix 2): expected exactly 1 non-archived row with 'cycl' in the title, "
            f"found {len(cycling_rows)}: {cycling_rows}"
        )
    cyc = cycling_rows[0]
    print(f"Fix 2: setting {cyc['title']!r} ({cyc['id']}) Status: {cyc['status']} -> Done")
    notion_request(
        "PATCH",
        f"/pages/{cyc['id']}",
        {
            "properties": {
                "Status": {"select": {"name": "Done"}},
                "Last Updated": {"date": {"start": today}},
            }
        },
    )
    _, check = notion_request("GET", f"/pages/{cyc['id']}")
    check_status = check["properties"].get("Status", {}).get("select", {})
    check_status = check_status.get("name") if check_status else None
    if check_status != "Done":
        sys.exit(f"ABORT (fix 2): updated but re-fetch shows Status={check_status!r}, not 'Done'")
    print(f"Fix 2: confirmed -- {cyc['title']!r} Status is now Done.")

    print("Both fixes applied and verified.")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - top-level safety net for CI logs
        print(f"::error::notion-manual-fixes-2026-09-06.py failed: {exc}")
        sys.exit(1)

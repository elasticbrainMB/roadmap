# _TEMPLATE — pointer file shape

Copy this shape for every new `projects\*.md`. Keep the fields identical
across every project — this is the one thing worth being boring about.

---
name: ""                # if graduating from BACKLOG.md, reuse that
                        # heading's exact text -- the Notion sync
                        # matches rows on it
status: ""              # one of: planned | active | paused | done
                        # sketched ideas live in BACKLOG.md, not here
disk_location: ""        # empty string if none yet
claude_project: ""       # empty string if none
canonical_status_file: "" # link/path to that project's own STATE.md or equivalent
last_synced: ""          # date this pointer file was last checked against the real thing
---

One or two sentences, plain language, what this project is and why it
exists. Nothing operational — that lives at `canonical_status_file`.

**This text becomes the Description column in the Notion status
dashboard verbatim, the first time this project is synced there.**
After that first sync it's left alone by every script -- Matt can
polish the wording directly in Notion, or edit it here, without
either side clobbering the other. Keep it to one or two sentences;
that's the whole point of it living separately from
`canonical_status_file`.

---
**Gotcha (found 2026-09-05):** the Notion sync workflow only fires on a
push that touches `BACKLOG.md` or `projects/**.md`
(`.github/workflows/notion-backlog-sync.yml`). Editing `STATE.md` alone —
even to fix wording that was blocking a drop via the sync script's own-title safety net —
does not re-run it. After a STATE.md-only fix, touch a file in that path
set too, or the fix sits unsynced until some unrelated project change
happens to push again.

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

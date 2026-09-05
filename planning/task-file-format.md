# task-file-format — planning document

**v0.1, 2026-09-04.** Answers `planning\dev-environment.md`'s open
question 3 — "What a task file contains, exactly. The seven work-package
items are the starting point; the file shape is not designed yet" (§9,
§10). A dated note pointing here has been added to that document rather
than folding this into it, so the design lives at one link.

Starting point: the seven items `caddy-autonomy-plan.md` §2 already
defined as what makes a work package runnable unattended, unchanged, plus
what `planning\dev-environment.md` §5 already named as reused without
change — the `verify-draft.ps1` / `verify-brief.ps1` grading pattern,
`invoke-model.ps1` and `config\model-caps.json` for spend control,
branch-per-run isolation, and `#run-logs` / `#decisions` / Notion for
notification.

---

## 1. The file

One task file per queued run. YAML front matter, then plain-language
context a person reads once and the runner never parses:

```yaml
---
id: ""                 # short slug — becomes the branch-name suffix and the report filename stem
project: ""             # which project's rules this run executes under, e.g. "caddy", "model-version-review"
goal: ""                 # one sentence, plain language
check: ""                # path to the script that decides pass/fail; must exist before the run starts
inputs: []               # paths or values the run needs already in place — verified at start, never assumed
scope: []                # exact paths this run may write to; a write outside this list is a stop
budget_dollars: 0.00
budget_minutes: 0
stop_conditions: []      # this run's own, beyond the four standing ones below
decision_list: []        # questions this run will NOT answer — it stops and reports these instead
created: ""              # date, and who queued it — Matt, or which thread
status: "queued"         # queued | running | done | stopped | error
---
```

Plain-language context, one or two sentences, for anything the fields
above don't make obvious.

**The four standing stop conditions apply to every task file without being
restated in it** — they're the runner's, not the file's: budget cap hit,
wall-clock cap hit, a write outside `scope`, or a dependency that dies
mid-run (`caddy-autonomy-plan.md` §4). A task file's own `stop_conditions`
are for anything specific to that run, on top of those four.

**The stop-rule threshold — three consecutive no-progress attempts, five,
or ten — is deliberately not filled in here, because it isn't settled
anywhere yet.** `planning\dev-environment.md` §9 and §10 track that
separately; this file shape doesn't take a position on the number.
Whichever the runner ends up enforcing applies uniformly, the same way none
of the four standing conditions above are per-file either.

## 2. How the seven items map onto the fields

| `caddy-autonomy-plan.md` §2 item | Field |
|---|---|
| 1. A goal with a check evaluable without Matt | `goal` + `check` |
| 2. Inputs that all exist before it starts | `inputs` — the runner verifies each, doesn't assume |
| 3. Scope — exact paths it may write to | `scope` |
| 4. A budget — dollars and wall-clock | `budget_dollars`, `budget_minutes` |
| 5. Stop conditions | The four standing ones, plus this file's own `stop_conditions` |
| 6. Outputs — the artifact plus a report in a fixed shape | Not a field — see §3 |
| 7. The decision list | `decision_list` |

Item 6 isn't a field because it's the runner's output, not the queue's
input — every run gets the same report shape regardless of what the task
file asked for.

## 3. The report

Written back into the same task file — front matter `status` flips to
`done` / `stopped` / `error`, a `## Report` section appended below the
context paragraph — not a separate file. One file is the whole record of a
run, queued through closed. Fixed shape:

- what ran, start and end time
- the `check` result — pass or fail, and why
- actual spend against `budget_dollars`
- anything in `decision_list` that needs Matt, or "none"
- a one-line summary, the same line posted to Discord

**Posting**: one line to `#alerts` always (muted — the log). If
`decision_list` came back non-empty, or the run stopped or errored, also
one message to `#decisions` (pings Matt) — mirrors
`caddy-autonomy-plan.md` §6's split, applied at the task-file level rather
than per-project.

## 4. Where the queue lives — not decided here

**`planning\dev-environment.md`'s own open question 4**: whether the queue
folder lives inside the project a task drives (`caddy\queue\`,
`model-version-review\queue\`) or at the roadmap level
(`C:\automation\queue\`, each file naming its own target project via the
`project` field). This document assumes the field exists either way — the
`project` key above works under either answer — but doesn't pick one.

**[VERIFY WITH MATT]** when the first real queue gets built — likely
during model-version-review's own build, since that project's task file
would be the first one anyone actually writes.

## 5. What this doesn't settle

- **The stop-rule threshold** (§1, above; `planning\dev-environment.md`
  §9–10).
- **Where the queue folder lives** (§4).
- **Whether `status` transitions are the runner editing the file in place,
  or a separate report file with a pointer back to it** — assumed to be
  in-place editing above, for the "one file is the whole record" reason in
  §3, but not tested against how Task Scheduler actually invokes a
  PowerShell script that needs to edit its own trigger file.
  **[VERIFY]**

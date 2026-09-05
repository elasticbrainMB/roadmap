# model-version-review — planning document

**v0.1, 2026-09-04.** Written the same day `planning\dev-environment.md`
(v0.3) named this as its leading second-project candidate, in its own §6.
This document is what moves the idea from Sketched to Planned, per this
repo's own lifecycle in `CLAUDE.md`. `BACKLOG.md`'s matching entry is
removed in the same sitting, and `STATE.md`'s row is updated.

Written from a read of `C:\automation\caddy` (`scripts\invoke-model.ps1`,
`scripts\step5-baseline.ps1`, `scripts\cmp-answer.ps1`, `eval\`,
`config\model-caps.json`, `STATE.md`, `caddy-autonomy-plan.md`) and
`C:\automation\roadmap` (`STATE.md`, `BACKLOG.md`,
`planning\dev-environment.md`) on 2026-09-04. Everything asserted about
disk was read from disk.

**Lifecycle: Planned.** Pointer file at `projects\model-version-review.md`,
`disk_location` empty — no folder yet.

---

## 1. What this project is

New Qwen and GLM releases keep shipping with no process in place to decide
whether Matt should switch. Right now that decision would take a
from-scratch bakeoff each time. This project turns it into a repeatable
check: run a candidate model's release against the same fixed questions the
caddy already uses to grade its own local model, score the answers against
the same frozen baseline, and hand Matt a pass rate instead of a guess.

**Why `dev-environment` picked this as its second project**
(`planning\dev-environment.md` §6 — carried here, not restated): the output
is a benchmark result a script can grade, which is the routing principle
`PRINCIPLES.md` names — "route on verifiability, not on how hard the task
looks" — and it recurs, so `dev-environment`'s queued runner gets exercised
on a real schedule instead of run once.

## 2. What already exists to build on

Two different scripts do adjacent work, and they are not the same tool —
worth being precise about, since `planning\dev-environment.md` §6 describes
them together as "the caddy's own `eval\` harness."

**`step5-baseline.ps1`** (`caddy\scripts\`) runs a table's fixed question
set (`eval\q-<table>.txt`) against one named model at temperature 0, and
saves every answer plus timing and token counts to
`eval\api-<table>-<tag>-<date>.json`. Its `-Model` and `-Endpoint`
parameters already let it point at a different **local** model — a newer
local Qwen build is a drop-in — but it only speaks Ollama's own
`/api/chat`. It cannot call OpenRouter, so it cannot run a GLM candidate as
written.

**`invoke-model.ps1`** (`caddy\scripts\`) is the general-purpose wrapper
`planning\dev-environment.md` §7 already flagged as "caddy-only but
general." It already speaks **both** providers through the same parameters
(`-Provider ollama` / `-Provider openrouter`), and it already has the three
things an unattended run needs that `step5-baseline.ps1` doesn't: per-call
and per-day dollar caps read from `config\model-caps.json` (currently
64,000 tokens/call, $0.75/run, $1.50/day), a single JSONL call log
(`records\runs\model-calls.jsonl`), and retry-with-backoff on OpenRouter
5xx responses. **This is the right foundation for calling a GLM candidate**,
not `step5-baseline.ps1` as it stands.

**`cmp-answer.ps1`** (`caddy\scripts\`) is the grading logic, and it's the
right comparison: exact match, then whitespace-normalized match, against
the most recent frozen `api-<table>-t00-np-*.json` baseline for that table.
**It's also entirely manual** — one question at a time, the candidate's
answer pasted from the clipboard by hand. Fine for spot-checking a local
model inside Open WebUI; not a shape a scheduled task can run unattended.

**The six tables' question sets and frozen baselines already exist and are
usable as-is**: `eval\q-metallica.txt`, `q-secret_agent.txt`,
`q-white_water.txt`, `q-tron.txt`, `q-big_bang_bar.txt`, `q-ac_dc.txt`,
graded against the matching `api-<table>-t00-np-*.json` files already on
disk.

## 3. What has to be built

Corrected from `planning\dev-environment.md` §6's "reuses the caddy's own
`eval\` harness ... unchanged" — the harness supplies the right pieces, not
a working pipeline, once you read past the two script names:

1. **A loop that replaces the manual clipboard step.** Something that plays
   the combined role of `step5-baseline.ps1` and `cmp-answer.ps1`, but
   calls `invoke-model.ps1` per question (so either provider works) and
   grades every answer against the frozen baseline automatically instead of
   one at a time by hand.
2. **Nothing new for spend control or logging.** `invoke-model.ps1` already
   caps and logs every call, local or OpenRouter — a run through several
   tables' worth of questions is already bounded by the existing
   `model-caps.json`.
3. **A report in a fixed shape** — pass rate per table, per candidate
   model, against the current baseline. This is item 6 of the work-package
   definition this project inherits (`caddy-autonomy-plan.md` §2); see also
   `planning\task-file-format.md`, written alongside this document.
4. **A release-detection trigger.** Something has to notice a new Qwen or
   GLM release exists before a run is worth queuing. Nothing on disk does
   this for models specifically today — infra-watch tracks software and
   package updates, not model releases. This is the crux of §4.

## 4. The open question — not decided here

**Carried from `BACKLOG.md` and `planning\dev-environment.md` §6 and §10
item 1 — "the first live question."**

Does model-version review live as a second collector inside infra-watch, or
as its own project?

| | Argument |
|---|---|
| **Shared, inside infra-watch** | Release-detection overlaps — infra-watch already watches for updates on a weekly schedule and already posts a risk assessment to Discord. A model release is the same shape of event. |
| **Separate project** | The deliverable is a different shape — a benchmark pass rate against a frozen question set, not a do-now / schedule / defer risk decision. infra-watch's report format and check logic are built around applying or deferring an update, not running an eval. |

**Not decided here.** Matt's call — flagged, not resolved.

## 5. What this project should not become

- **Not a framework before a second real use exists.** `PRINCIPLES.md`'s
  rule of two applies here the same way `planning\dev-environment.md` §7
  applies it to itself: extract shared plumbing (a general "run these
  questions through this model and grade them" script) once there's a
  second thing that needs it, not in anticipation.
- **Not a model grading its own release.** The candidate model answers
  questions; grading is the existing exact/normalized string comparison
  against a frozen baseline — a script, never another model call. Per
  `PRINCIPLES.md`: "a model never grades its own output."
- **Not the decision to switch.** This produces a pass rate. Whether that's
  good enough to change what `caddy-server.js` actually calls stays Matt's,
  the same way freezing a rules document does.

## 6. Open questions

1. **Collector or own project** — §4. The first live question.
2. **Whether the six existing table question sets are the right yardstick
   for a general model swap**, or whether they're specific enough to the
   caddy's own rules content that a model could score well on caddy
   questions and still be a worse general choice. **[VERIFY WITH MATT]** —
   a judgment call this reading of disk can't settle, not a fact.
3. **Model names and OpenRouter IDs for current Qwen and GLM releases** —
   **[VERIFY]** at build time, the same convention `caddy-autonomy-plan.md`
   already applies to its own model references.
4. **Whether this needs the queued-runner task-file shape at all**, or
   whether — being a recurring scheduled check rather than a one-off
   drop-in task — it's closer to infra-watch's own weekly-Task-Scheduler
   pattern than to the "Matt drops a file before bed" queue
   `dev-environment` is designing. Related to §4; not resolved by it.

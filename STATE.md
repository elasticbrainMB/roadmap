# STATE.md — roadmap index

Fast orientation across everything currently running or sketched. Each
project's real status lives at its own link — this table is a summary,
corrected here whenever a project's status changes materially, per the sync
discipline in `CLAUDE.md`.

_Last confirmed with Matt: 2026-09-05_

| Project | Status | Where | Notes |
|---|---|---|---|
| Pinball caddy | Active | `C:\automation\caddy`, claude.ai project *Vpin Skills Improvement* | See `projects\caddy.md` |
| infra-watch | Active | `C:\automation\infra-watch`, GitHub `elasticbrainMB/infra-watch` | v1 built and running weekly via Task Scheduler. See `projects\infra-watch.md` |
| vpin skill-building (practice tables) | Paused | No folder yet — Matt will create one when he revisits this project | A vibe-coded project addressing a scenario he posted to r/virtualpinball (table drills for individual skill-building). A somewhat-usable version exists; needs more tweaks before it's where he wants it. Corrected 2026-09-05 — was listed Active |
| project-status | Active | `C:\automation\project-status` | Mid-build — see `projects\project-status.md` |
| Model-version review (Qwen / GLM) | Planned | No folder yet — see `planning\model-version-review.md` | Filed Planned 2026-09-04, moved out of `BACKLOG.md`. Reuses caddy's `invoke-model.ps1` and the six tables' `eval\` question sets; one open question on where it lives — see the planning doc |
| Cycling-day rating | Active | n8n workflow `UC1 - Cycling Day Rating`, no folder | **Live and running daily at 06:00 CT**, posting to Discord `#cycling`. Corrected 2026-09-04 — `BACKLOG.md` had listed it Sketched; it has been running since at least 2026-08-19 |
| dev-environment | Planned | No folder yet — see `planning\dev-environment.md` | Shared foundation across projects, and a queued runner so agentic work can start without Matt. Scoped 2026-09-04 |
| Podcast triage, Strava construction, dinner survey, beehiiv (content + ops) | Sketched | — | See `BACKLOG.md`. Why the beehiiv items exist at all — see `CONTEXT.md` |

**Status vocabulary is the lifecycle in `CLAUDE.md`:** Sketched, Planned,
Active, Paused, Done.

**Dropped from this table, 2026-09-03, Matt's call:**
- **Job search automation** — runs as a scheduled task and its own claude.ai
  project already; not tracked here. He may bring it back onto this roadmap
  later.
- **Distributed inference network** — no longer being pursued.
- **eGPU cooling** — not a project; was on the first draft in error.

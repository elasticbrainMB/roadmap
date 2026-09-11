# STATE.md — roadmap index

Fast orientation across everything currently running or sketched. Each
project's real status lives at its own link — this table is a summary,
corrected here whenever a project's status changes materially, per the sync
discipline in `CLAUDE.md`.

_Last confirmed with Matt: 2026-09-10_

| Project | Status | Where | Notes |
|---|---|---|---|
| Pinball caddy | Active | `C:\automation\caddy`, claude.ai project *Vpin Skills Improvement* | See `projects\caddy.md` |
| infra-watch | Active | `C:\automation\infra-watch`, GitHub `elasticbrainMB/infra-watch` | v1 built and running weekly via Task Scheduler; a full round of stack updates completed, confirmed current and no open items 2026-09-10. See `projects\infra-watch.md` |
| vpin skill-building (practice tables) | Paused | No folder yet — Matt will create one when he revisits this project | A vibe-coded project addressing a scenario he posted to r/virtualpinball (table drills for individual skill-building). A somewhat-usable version exists; needs more tweaks before it's where he wants it. Corrected 2026-09-05 — was listed Active |
| project-status | Active | `C:\automation\project-status` | Live — Notion dashboard sync (backlog sync + per-project hooks) confirmed running end to end, no open items 2026-09-10. See `projects\project-status.md` |
| Cycling-day rating | Done | n8n workflow `UC1 - Cycling Day Rating`, no folder | **Complete as of 2026-09-06**, confirmed by Matt — built and run across its own chat/Cowork threads directly, never as a project with a folder. Was live and posting daily to Discord `#cycling` since at least 2026-08-19 |
| dev-environment | Active | `C:\automation\dev-environment` | **Graduated Planned → Active 2026-09-10.** Shared foundation across projects, rebuilt around OpenClaw 2.0 as the front door and the runner for model-in-the-loop work. Phase 0 of 3 in progress; no repo yet. See `projects\dev-environment.md` |
| Strava construction, dinner survey, beehiiv (content + ops) | Sketched | — | See `BACKLOG.md`. Why the beehiiv items exist at all — see `CONTEXT.md` |

**Status vocabulary is the lifecycle in `CLAUDE.md`:** Sketched, Planned,
Active, Paused, Done.

**Dropped from this table, 2026-09-03, Matt's call:**
- **Job search automation** — runs as a scheduled task and its own claude.ai
  project already; not tracked here. He may bring it back onto this roadmap
  later.
- **Distributed inference network** — no longer being pursued.
- **eGPU cooling** — not a project; was on the first draft in error.

**Dropped from this table, 2026-09-05, Matt's call:**
- **Podcast episode-rating idea** — dropped before being scoped; was a `BACKLOG.md` sketch only (rate new episodes 1-5 for listen-worthiness).
- **Qwen/GLM model-version review track** — dropped before reaching Active. Scoping work stays on disk for reference; the pointer file has been moved out of `projects\` for Matt to remove. *(Phrased to avoid the literal BACKLOG/pointer-file title text here on purpose -- see the note below.)*

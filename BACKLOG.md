# BACKLOG.md — Sketched ideas only

Ideas with no scope yet. An entry leaves here the moment it becomes
**Planned** — at that point it gets a `planning\<name>.md` document and a
`projects\<name>.md` pointer file, and this entry is deleted, not archived.
Nothing should ever be listed here and in `projects\` at the same time.

## Model-version review track (Qwen / GLM)
New Qwen and GLM releases shipped during the caddy build with no resource
for deciding whether to switch. Different problem from infra-watch's
version tracking — a new model needs an eval run against real work, not a
changelog read. The caddy's own `eval\` harness (`cmp-answer.ps1`,
`step5-baseline.ps1`) is the natural starting point if this gets built.
Open question, unresolved: does this become a second collector inside
infra-watch, or its own project? Argument for shared: release-detection
overlaps. Argument for separate: the output is a benchmark result, not a
decision queue — a different shape of deliverable.

## Cycling-day rating
3–5 day weather-based cycling-viability rating. Named in
`local-inference-stack` notes as slotted first in the original use-case
ordering — hasn't been built yet as of this writing.

## Podcast episode triage
Rate new podcast episodes 1–5 on listen-worthiness from transcripts.
Rubric not yet defined.

## Strava construction-route flagging
Flag active construction on regular cycling routes for advance detour
planning, rather than mid-ride rerouting. Deferred behind the four-project
core set in the original local-inference-stack roadmap.

## Dinner survey
Named as one of four projects sharing the unattended-work runner in
`Dev environment architecture ideation v2/v3`. No further detail captured
in memory or project docs as of this sitting — `[VERIFY WITH MATT]` what
this actually is before treating it as more than a name.

## beehiiv newsletter about his projects
Future-proofing exercise as of 2026-09-03, not a committed build. Possibly
splits into content-development, operations/SEO-AEO, and reporting
sub-projects that would need to read each other and read upstream project
status. If it gets built: start as one folder, split later using the same
pattern this project itself uses — a nested `STATE.md` one level down,
treated as a single entry from this project's own table, exactly the way
this table treats caddy as one line today.

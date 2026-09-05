# Cowork handoff — dev-environment

**Written 2026-09-04**, to start a fresh Cowork thread in the **Roadmap**
claude.ai project. Assume no prior conversation.

**This handoff points rather than duplicates**, per the roadmap repo's own
rule that content lives at the link. Read the files it names.

---

## 1. Your role

**You do reasoning, planning, scope and review.** You read the repositories
directly, write the prompts Matt pastes into Claude Code, and review session
logs afterwards against disk. **Claude Code, on the mini PC, does the work on
disk** — new thread per sitting. **Matt makes every final call** on design,
machine configuration and governing documents.

**Matt's constraints:** full-time job, two kids, several other interests.
**He is optimising for his own attention and time**, not for elegance. He
described wanting to start work before bed and check in from his phone
between meetings — handed results, or the blockers only he can clear.

## 2. First moves

**Request folder access:**

```
mcp__remote-devices__device_request_folder_access
  C:\automation\roadmap
  C:\automation\caddy
```

Roadmap is the project you own. Caddy is where every reusable pattern was
built and proven, including the `eval\` harness the first project will use.
Add `C:\automation\project-status` or `C:\automation\infra-watch` only if a
question actually needs them.

**Then read, in this order:**

| File | Why |
|---|---|
| `roadmap\planning\dev-environment.md` | **The plan. This is your work.** v0.3 |
| `roadmap\STATE.md` | What exists across all projects, one table |
| `roadmap\CLAUDE.md` | The lifecycle, the sync discipline, what this repo is and isn't |
| `roadmap\PRINCIPLES.md` | Standing rules, each with the project it was learned on |
| `caddy\STATE.md` | Where the caddy actually is |
| `caddy\caddy-autonomy-plan.md` | The prior plan. §2 (work packages), §3 (routing), §4 (stop rules) are what dev-environment inherits |

**Do not read caddy's charter, roadmap or amendments log up front** — 346 KB
between them. Read them only when a specific question needs them.

### Bridge mechanics, learned the hard way

- **`git --no-optional-locks status`.** A plain `git status` over the bridge
  writes `.git/index.lock`, and the bridge cannot delete files, so it leaves
  a stale lock that blocks Matt's next git command.
- **To write a file to the mini PC:** `SendUserFile`, then
  `device_commit_files` with the returned uuid. **Not shell heredocs** —
  backslashes in Windows paths have collapsed that way twice on this setup.
- **Verify after every write:** no byte-order mark, zero carriage returns,
  backslash paths intact. `head -c 3 f | od -An -tx1` and `tr -dc '\r' < f | wc -c`.
- **Read-only over the bridge wherever possible.**

## 3. Conventions that hold across these projects

- **Sittings are 30–45 minutes**, one thing at a time, hard stop conditions.
  New Claude Code thread each.
- **One stop per sitting**, placed where Matt's decision changes the output.
  Questions to him only when the answer changes the deliverable.
- **Every Code prompt is one pasteable block, self-contained**, with a
  standing-checks header: verify against disk before acting, treat prompt
  text as requirements not paste-ready content, report contradictions before
  drafting, guard every edit by asserting the original text at the target
  line, cite nothing from memory.
- **The severity bar goes in every prompt.** Tier 1 — stops a run, puts a
  wrong fact into a deliverable, weakens a guardrail, or exposes a secret —
  report immediately and stop. Tier 2 fails loudly whenever it happens, one
  line in the close. Tier 3 is wording and tidiness, file and line number
  only. **Only Tier 1 interrupts.**
- **Deliver prompts as files**, then commit them. Long verbatim blocks have
  failed to survive relay on this setup before.
- **Correct a document with a dated supersede-in-place note**, never a silent
  overwrite.
- **Review every session log against disk**, not by reading the log. That
  caught things the log did not say, repeatedly.
- **Secrets live at `C:\automation\secrets\*.env`**, outside every repo.
  Never printed, never in a command line.

## 4. Where things stand

Four projects, all on the mini PC, all with private GitHub repos under one
scoped PAT.

| | |
|---|---|
| **caddy** | Six tables frozen, all with live briefs. Phase F (latency, voice) in its own thread. Phase G on hold. **Phase E measured the whole point: interruptions per table went from ~7 to about 1** |
| **infra-watch** | v1, running weekly via Task Scheduler |
| **project-status** | Notion mirror, live. GitHub Actions calls the Notion API on a successful run. Disk stays the truth |
| **cycling-day rating** | Live n8n workflow, daily 06:00 CT to Discord `#cycling`. No folder |
| **roadmap** | The index. Lifecycle, `PRINCIPLES.md`, backlog |

**The gap dev-environment exists to close:** deterministic scheduled jobs
already run unattended; **agentic work does not.** Every drafting, fixing and
reconciling job is still a sitting Matt starts and watches.

## 5. What Matt has decided

All 2026-09-04, all in `planning\dev-environment.md` §2:

- **First increment: prove the pattern on a second project.** Not
  housekeeping, not full autonomy.
- **Target shape: the queued middle ground.** Matt drops a task file; a
  scheduled run picks it up under existing caps and stop rules and posts the
  result or the blocker. It does nothing when the queue is empty — **it fails
  safe, which is why it is the cheap version.**
- **The two combine.** The second project is built *as a queued package*, so
  one build tests both.
- **Leading project: model-version review (Qwen / GLM).** Still Sketched —
  it becomes Planned when it has its own `planning\` document.
- **Filing: Planned**, pointer at `projects\dev-environment.md`, no backlog
  entry.

## 6. Your first tasks

**1. Scope model-version review into `planning\model-version-review.md`**, and
move it out of `BACKLOG.md` when it lands there. One open question comes with
it, carried from the backlog: **second collector inside infra-watch, or its
own project?** Shared release-detection argues one way; a benchmark result
being a different shape of deliverable than a decision queue argues the other.

**2. The stop-rule threshold — know where it stands, don't chase it yet.**
The architecture doc says ten consecutive loops; the plan says three
consecutive attempts with no check passing. **Matt's leaning of 2026-09-04 is
five**, stated as *"let's start with"* and then deferred — a leaning, not a
filed decision. **He deferred it deliberately and that is fine**: the queued
runner is not being built yet, so nothing is blocked. **It must be settled
before that build begins, not during it.**

**3. Design the task-file shape.** The seven work-package items in
`caddy-autonomy-plan.md` §2 are the starting point; the file format is not
designed.

## 7. Housekeeping waiting in the roadmap repo

**Uncommitted at handoff time**, all legitimate work nobody has recorded:

```
 M STATE.md
 D planning/infra-watch.md
 M projects/infra-watch.md
?? Claude outputs/
?? planning/dev-environment.md
?? projects/dev-environment.md
?? projects/project-status.md
```

That is infra-watch's Planned→Active transition, project-status's pointer,
and today's dev-environment files. **Also decide whether `Claude outputs\` is
tracked content or ignored scratch** — it currently holds a Notion outline,
and its name breaks the lowercase convention the other folders follow.

## 8. Two things worth carrying

**The sync discipline has slipped twice in one day, on a four-day-old repo.**
`BACKLOG.md` listed cycling-day rating as Sketched while it had been running
daily since at least 19 August, and the transition above sat uncommitted.
The rule in `CLAUDE.md` is sound — touch the matching file close to the
change, not batched later from memory. **Whether it needs a mechanism or just
attention is an open question in the plan, not a decision anyone has taken.**

**A candidate `PRINCIPLES.md` entry, now learned twice:** *a backup that
isn't exercised isn't a backup.* 33 caddy commits sat unpushed for two weeks
against a remote created in Phase A specifically to hold them — found only
when project-status went looking for a different thing.

## 9. Working with Matt

- **Plain language, always.** No jargon, acronyms or technical terms unless
  he used the term first or asked for depth. This does not relax as things
  get complex.
- **Push back when it improves the output.** He asks for this directly, and
  he has overridden it correctly more than once.
- **Say what a recommendation costs**, not only what it buys.
- **Verify before asserting.** He has direct evidence to hand and will check.
  The `[VERIFY WITH MATT]` and `[VERIFY]` markers are his own convention —
  use them rather than guessing.

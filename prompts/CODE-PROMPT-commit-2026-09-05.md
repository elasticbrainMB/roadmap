# Code prompt — commit today's roadmap work, and the caddy correction, as two scoped commits

**Standing checks, every prompt:** verify against disk before acting — the
file lists below are what Cowork observed a few minutes ago, not a
guarantee of the current state. Treat this prompt as a set of requirements,
not paste-ready content. If `git status` in either repo doesn't match what's
described below, stop and report the difference before doing anything —
don't guess at what changed or improvise a different file list.

**Severity bar.** Tier 1 — committing a file not on the list below,
committing anything under `C:\automation\secrets\`, or any destructive git
operation (reset --hard, force push, amend) — stop immediately and report,
don't attempt a fix. Tier 2 — wrong commit message, wrong repo, anything
that needs a note but isn't Tier 1 — fix if you can, one line in the close.
Tier 3 — wording only. **Only Tier 1 interrupts.**

This is two independent git repos. Do both. Nothing here touches
`git commit --amend`, `reset`, `rebase`, or any force-push — plain commits
only.

---

## 1. `C:\automation\roadmap` — this thread's work

```
cd C:\automation\roadmap
git status
```

**Confirm these, and only these, are the modified/untracked files before
staging** (there will also be `planning\infra-watch.md` deleted,
`projects\infra-watch.md` modified, `projects\project-status.md`
untracked, and a `Claude outputs\` folder untracked — **leave all four of
those alone**, they're separate, unrelated housekeeping, not part of this
commit):

```
git add BACKLOG.md CLAUDE.md STATE.md CONTEXT.md ^
  planning\dev-environment.md planning\model-version-review.md ^
  planning\task-file-format.md planning\HANDOFF-cowork-dev-environment.md ^
  projects\dev-environment.md projects\model-version-review.md ^
  prompts\CODE-PROMPT-commit-2026-09-05.md
```

Run `git diff --cached --stat` and confirm it lists exactly those files —
nothing from the excluded four, nothing else. Then:

```
git commit -m "Scope dev-environment and model-version-review; correct vpin/Strava/dinner-survey/beehiiv status; add CONTEXT.md"
```

## 2. `C:\automation\caddy` — the Strava/MnDOT correction only

```
cd C:\automation\caddy
git status
```

**This repo has a large amount of unrelated uncommitted work** (build
guides, session logs, records, script changes) — none of it is part of
this commit. Stage only:

```
git add openclaw-environment-spec-v1.md caddy-autonomy-plan.md
```

Run `git diff --cached --stat` and confirm it lists exactly those two
files. Then:

```
git commit -m "Correct UC7 Strava provenance: MnDOT 511 was unvetted AI ideation, not Matt's own scoped design"
```

**Do not stage or commit anything else in this repo.** The rest of what
`git status` shows here is a separate, much larger cleanup that needs its
own review — flag it in your close-out, don't fold it into this commit.

---

## Close-out

One line per repo: commit hash, and confirmation the `git diff --cached
--stat` check matched expectations before each commit. If either check
didn't match, say what actually got staged instead of what to do about it —
that's Matt's call.

# Code prompt — finish infra-watch's pointer file, fix a second latent casing bug, and push the Description-column work

**Standing checks, every prompt:** verify against disk before acting — the
file lists below are what Cowork observed a few minutes ago, not a
guarantee of the current state. Treat this prompt as a set of
requirements, not paste-ready content. If `git status` doesn't match what's
described below, stop and report the difference before doing anything —
don't guess at what changed or improvise a different file list.

**Severity bar.** Tier 1 — committing a file not on the list below,
committing anything under `C:\automation\secrets\`, any destructive git
operation (reset --hard, force push, amend), or pushing before both
commits below are verified staged correctly — stop immediately and report,
don't attempt a fix. Tier 2 — wrong commit message, wrong repo, anything
that needs a note but isn't Tier 1 — fix if you can, one line in the close.
Tier 3 — wording only. **Only Tier 1 interrupts.**

One repo (`C:\automation\roadmap`), two commits, then a single push.
Nothing here touches `git commit --amend`, `reset`, `rebase`, or force-push.

---

## Context — why this exists

A prior session added a Description column to the Notion project-status
dashboard and committed the change locally (commit `8ce9844`,
"Add a Description column to the Notion status dashboard") but
deliberately did **not** push it. `projects\infra-watch.md` was — and may
still be — committed with stale content (`status: "planned"`, and
`name: "infra-watch"` lowercase) while Matt had a newer version sitting
uncommitted locally with the status fixed but the lowercase-name casing
bug still present. That casing mismatch is the exact bug that already
created one duplicate "infra-watch" row in Notion once before (see
`C:\automation\project-status\STATE.md` section 8) — the sync matches
Notion rows on exact title text, and Notion's real row is titled
"Infra-Watch", not "infra-watch". Pushing with that file still stale or
still mismatched would recreate the duplicate.

While closing this out, a second instance of the identical bug was found:
`projects\project-status.md`'s `name` field is `"project-status"`
(lowercase, hyphenated), but its Notion row is titled "Project Status".
It hasn't caused a visible problem yet only because that row's
Description was already seeded by hand — but it means the sync silently
no-ops on that row (`seed_description_only` looks up the row by exact
title and finds nothing), so any future re-seed would need this fixed
first anyway. Fix it now while the same class of bug is already the
focus.

## 1. `C:\automation\roadmap` — verify state, then two commits

```
cd C:\automation\roadmap
git status
```

**Confirm this matches** (there may also be a `Claude outputs\` folder and
a `_to_delete\` folder untracked — leave both alone, they're unrelated
pre-existing housekeeping, not part of either commit here):

```
 D planning/infra-watch.md
 M projects/infra-watch.md
?? "Claude outputs/"
?? _to_delete/
```

If `projects/infra-watch.md`'s working-tree diff does **not** show
`status: "active"` (i.e. Matt's pending fix is gone, already committed, or
changed shape), stop and report — don't guess at what to commit.

### Commit A — finish graduating infra-watch's pointer file (Matt's own pending edit, as-is)

Stage exactly Matt's already-pending change, unmodified — do not touch the
body prose:

```
git add planning/infra-watch.md projects/infra-watch.md
git diff --cached --stat
```

Confirm that lists exactly those two paths (one deletion, one
modification), nothing else. Then:

```
git commit -m "Graduate infra-watch pointer file to Active"
```

### Commit B — fix both latent name-casing bugs before they ever bite

Using a plain-text edit (not a wholesale rewrite — only the `name:` line
in each file changes), fix:

- `projects/infra-watch.md`: `name: "infra-watch"` → `name: "Infra-Watch"`
- `projects/project-status.md`: `name: "project-status"` → `name: "Project Status"`

Both must exactly match their Notion row's title text (case, spacing,
punctuation) — confirm against Notion directly if there's any doubt,
don't assume this description is still accurate.

```
git add projects/infra-watch.md projects/project-status.md
git diff --cached --stat
```

Confirm that lists exactly those two paths. Then:

```
git commit -m "Fix pointer-file name casing to match Notion row titles exactly (infra-watch, project-status)"
```

## 2. Push, then verify

```
git push origin main
```

This will push both this session's two commits and the prior session's
`8ce9844`, and will trigger `notion-backlog-sync.yml` (it watches
`BACKLOG.md` and `projects/**.md`, and `8ce9844` already touched
`BACKLOG.md`).

After the push, confirm the workflow run succeeded (GitHub Actions API or
UI), then check the Notion Projects database (the MCP connector, if
available in this session, is the direct path — prefer it over browser
automation or a device-shell `curl`, which is blocked by an egress
allowlist from the mini PC's own shell):

- Exactly one "Infra-Watch" row, still Active, still the same Description
  it already had (the sync only fills Description if blank — it was not).
- Exactly one "Project Status" row, unaffected the same way.
- No new "infra-watch" or "project-status" (lowercase) rows were created.

If a duplicate appears anyway, **stop and report — do not delete or merge
rows yourself.** That's a sign this prompt's assumptions about current
Notion state were wrong, and Matt should see the actual state before
anything gets cleaned up.

---

## Close-out

One line per commit: hash, and confirmation the `git diff --cached --stat`
check matched expectations before it was made. One line for the push
(succeeded / what failed). One line for the Notion verification (matched
expectations / what didn't). If `Claude outputs\` or `_to_delete\` are
still sitting there untracked, say so in one line — Matt's call on those,
not this prompt's.

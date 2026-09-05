# roadmap — build rules

**What this project is.** An index of projects, a set of standing rules that
apply across more than one of them, and a backlog of ideas without a project
yet. It does not run anything. If a task here starts looking like a script
or a schedule, stop — that's a different kind of project, and it should live
in its own folder the way caddy and infra-watch do.

## The one rule that matters most

**A pointer file's shape stays stable.** `projects\_TEMPLATE.md` defines the
fields every project entry carries. Once more than one thing reads a pointer
file — and the whole point of this project is that eventually more than one
thing will — a field added or removed without warning is a small breaking
change for whatever's reading it. Extend the template deliberately, not
per-project.

## Sync discipline

This project doesn't pull status from anywhere automatically. It's kept
current by one habit, borrowed from the caddy's own STATE.md maintenance
rule: **closing a chunk of work in a project folder that changes that
project's status, scope, or touches a rule that belongs in `PRINCIPLES.md`
also means touching the matching file here.** Small edit, done close to the
change, not batched up and reconstructed later from memory.

**This project's own `CLAUDE.md` and `PRINCIPLES.md` do not propagate
themselves outward automatically.** `C:\automation\caddy\CLAUDE.md` predates
this project and carries its own copies of several rules that now also live
in `PRINCIPLES.md` here — that's fine, it was written to be self-contained
on its own stated reasoning, and caddy's own file explicitly protects its
length ("anything added displaces something"). **Do not edit it to remove
the duplication without asking Matt first.** Treat `PRINCIPLES.md` here as
canonical for anything new, or anything that spans more than one project
going forward — not as license to go tidy up an existing project's working
file.

## Where things live

- `STATE.md` — human-facing index. A table plus short prose. Read this first.
- `CONTEXT.md` — why this roadmap is documented publicly at all (the
  beehiiv newsletter, the career goal behind it) and what that means for
  how a finished project gets written up. Read once; not project-specific.
- `PRINCIPLES.md` — standing rules, each one with which project it was
  learned on and why. Not a wishlist — only things already proven out.
- `BACKLOG.md` — **Sketched ideas only.** No scope, no document, no folder.
  An entry leaves here the moment it becomes Planned.
- `planning\*.md` — the scoped definition of a project that isn't built yet.
  Moves out to that project's own folder when it goes Active.
- `projects\*.md` — one pointer file per Planned or Active project. Fixed
  field set, per `_TEMPLATE.md`. The content lives at the link, not here.

## The lifecycle, in one line

**Sketched** (`BACKLOG.md`) → **Planned** (`planning\` + a pointer file) →
**Active** (own folder and repo; planning doc moves out, pointer stays).
Each state has exactly one home. If something appears in two of them at
once, that's a state that didn't finish transitioning, not a filing
preference — fix it rather than keeping both in sync.

Ideation for a Sketched idea happens as a chat or Cowork thread in this
project. **The thread is the workspace; the written entry is the record.**
Write it down as the thinking happens.

## Notion sync

`BACKLOG.md` and any `projects\*.md` with `status: planned` push to the
shared Notion Projects database on every commit that touches them
(`.github/workflows/notion-backlog-sync.yml`, `scripts/notion_backlog_sync.py`).
Same mirror-not-source relationship as the rest of this project's Notion
work: disk stays the truth, Notion is a window onto it.

**This is why the title-locking rule matters in practice, not just in
principle.** The sync finds a Notion row by exact title match. If an idea
graduates and its pointer file's `name` doesn't reuse the BACKLOG.md
heading text exactly, the sync can't tell it's the same idea -- it creates
a second row instead of updating the first.

If an idea skips the pointer-file stage entirely (goes straight to Active
with no folder yet, the way a pure n8n workflow can) its Notion row won't
get auto-updated by this sync, and won't get auto-dropped either as long
as it's still named somewhere in `STATE.md` -- that case stays a manual
correction, same as it was before this sync existed.

## Execution discipline

Lighter than caddy's, because there's less at stake here — but the shape
carries over: read before you write, verify a claim against the file it
should live in rather than trusting a summary of it, and end a chunk with a
short status note.

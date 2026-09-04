# PRINCIPLES.md — standing rules across projects

Each rule here has already been paid for once, on a real project. Learned-on
is included on purpose — a rule with no history is a guess wearing a rule's
clothes.

## Disk is the source of truth; other surfaces are mirrors
If a run needs Notion, Discord, or a claude.ai project doc to be reachable
in order to proceed, an outage of that surface becomes a failed run. Write
the real result to disk first; post or sync from there, after the fact,
never the other way around. *Learned on: caddy, from the Notion/Discord
design in `caddy-autonomy-plan.md`.*

## A model never grades its own output
Where a script can't check something and a model must, that's a separate
call with no shared history — preferably a different model than the one
that produced the work. *Learned on: caddy — a model checking its own draft
marked three missing rules as present; one reached a player as a wrong
answer.*

## Route on verifiability, not on how hard the task looks
The question that decides which model handles a step isn't complexity —
it's whether a script can check the answer. If yes: cheapest capable model,
escalate on repeated failure. If no and the cost of a wrong answer is low
and reversible: a mid-tier model, skimmed. If no and the cost is high (it
reaches a document or a person downstream): the best model, plus an
independent second pass, plus a person. *Learned on: caddy / the runner
architecture doc.*

## A gate states a decidable condition, not a count or an adjective
"Stop if more than one thing changed" passes the wrong things. "Read every
change and judge each better, worse, or neutral" doesn't. A check has to be
answerable by inspection, not by opinion. *Learned on: caddy's
`GUIDE-authoring-rules-docs.md` lineage.*

## Use the fact, not a proxy for it
A count or a position that another file owns goes stale — state the
property, not the number. `Measure-Object -Line` is not a line count; a file
being present is not evidence it's current. *Learned on: caddy, multiple
build guides, more than once.*

## Stop conditions are hard stops
Don't route around a failure to keep momentum. A failure is informative;
routing around it discards the information. *Learned on: caddy's execution
discipline, carried into infra-watch's stop-condition list.*

## The four API-calling hazards
Never `-s ... | Out-Null` on an API call — it hides a non-200. Inline JSON
to `curl.exe` fails; write the body to a file and use `-d "@body.json"`.
A BOM breaks JSON parsing in more than one tool that's been tested against
it — write UTF-8 without one. PowerShell's `-eq` compares strings
case-insensitively; byte equality needs `-ceq`. *Learned on: caddy, each one
the hard way, each one cited by chunk in `CLAUDE.md`.*

## A filename that asserts a state is a claim
Don't write a chunk name or a date into a filename before the thing it names
is actually true. *Learned on: caddy — a build guide targeted a
`-post-c35` filename before the step it named had run.*

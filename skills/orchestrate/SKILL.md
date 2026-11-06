---
name: orchestrate
description: >
  Decide whether delegation pays and coordinate bounded implementation or review
  with concise context and appropriate models. Use for explicit delegation,
  orchestration, executor/model routing, or reducing agent coordination cost.
  Ordinary multi-file implementation alone does not require this skill.
---

# Orchestrate

Use one implementer by default, including ordinary multi-file features.
Delegate only when bounded independent work or a focused review is likely to
save more than startup, context, and coordination cost. Keep final acceptance
with the supervising agent. A second provider is an option when useful, not a
prerequisite or a reason to repeat investigation.

## 1. Assess

Choose inline execution or a specific delegation boundary. File count alone
is not a delegation criterion. If working inline, follow the project's normal
workflow and skip the delegation steps below.

If delegating across unfamiliar modules, consider bounded read-only reconnaissance
when it avoids repeated discovery. Require only code anchors, relevant conventions,
and likely checks; feed that concise map to the implementation executor so it
does not repeat broad discovery. Skip this pass when the supervisor already
has those anchors.

Before an external dispatch motivated by cost or limits, inspect only relevant
providers. Record authentication, known remaining quota or spend cap, agentic
write capability, and whether a CLI shares the supervisor's quota. Treat quota
as unknown unless a tool or the user establishes it; never invent precision.

Done when: you have stated an explicit go/no-go and, when relevant, the
provider budget constraint in one line.

## 2. Break Down

Decompose the work into **end-to-end features**. One feature = one behavior,
screen state, model change, or service integration — roughly 30–90 minutes of
work. Split anything touching multiple screens or domains; never bundle UI
polish, persistence, networking, and navigation in one feature unless the
behavior requires it.

Every feature carries five fields:

- user-visible outcome
- likely files/areas
- acceptance matrix: happy path, adversarial/negative cases, side-effect
  invariants, and runnable checks
- risk class: routine, stateful, or safety-critical
- route (from step 3)

Keep this matrix in the delegation prompt or supervisor notes, not in a
temporary repository document unless the project explicitly requires one.

Done when: every feature has all five fields.

## 3. Route

Route each feature to the cheapest executor that can pass its acceptance checks:

| Work | Route |
| --- | --- |
| Architecture, product decisions, UI taste, ambiguous bugs, privacy/security invariants, final QA | Supervisor — never delegate the judgment |
| Codebase investigation, search, summarizing code | Cheap read-only subagent |
| Mechanical edits, refactors, compile-fix loops, tests-to-spec, boilerplate | Cheap implementation executor — small-model subagent or CLI agent |
| Stateful or safety-critical implementation after invariants are fixed | Strong external-provider executor; supervisor retains acceptance judgment |
| Independent review of a finished feature | Any executor that is not the feature's author |

Choose both a capability level and a provider:

- Reserve the supervisor's provider for decomposition, decisions, review
  aggregation, and final acceptance when its quota is constrained.
- Prefer an authenticated executor on a different paid provider, or a capable
  local model, when it can pass the same checks.
- Assume another CLI backed by the same account/provider consumes the same
  quota unless proven otherwise.
- Never trade away required capability merely to save tokens. Escalate before
  accepting repeated failures or weak evidence.
- Prefer a different provider for review than for authorship when available;
  independence is more valuable than model monoculture.
- When the supervisor's quota is constrained, route full review axes to other
  providers too. The supervisor aggregates their concise findings, inspects
  critical hunks, reruns decisive checks, and retains final acceptance.

Executor mechanics — model choice, CLI invocations, the delegation prompt
template, and the escalation ladder — live in
[references/delegation.md](references/delegation.md); read it before
dispatching.

Done when: the route names the provider/executor, explains why it is capable,
and records quota impact as known or unknown.

## 4. Delegate

One executor per feature. Sequential when features share files; parallel only
when files are disjoint or the work is read-only. A narrowly permissioned CLI
executor may work directly on the current feature branch when execution is
sequential, the worktree is clean, and neither the supervisor nor another
agent will edit it concurrently. Never let an executor edit the default branch.
Use an explicit git worktree for concurrent writers, broad-permission agents,
experimental/local models, or whenever the supervisor must keep using the
primary checkout.

Start subagents with fresh context (`fork_turns: none` where supported); choose
the smallest capable model explicitly. Keep issue text to relevant acceptance
criteria and link the required project docs instead of inheriting chat history.

The delegation prompt is self-contained — the executor knows nothing you
don't tell it. It carries seven parts: goal, files, constraints, out-of-scope,
acceptance matrix, runnable checks, and which project docs to read first.
It also declares the mode (`IMPLEMENT`, `INVESTIGATE`, or `REVIEW`) and source
precedence. For implementation, bound exploration, require an edit or an
explicit `BLOCKED` result, forbid plan-only completion, commits, and
opportunistic refactors, and define the evidence required for completion.

Before dispatch, lint the prompt: remove conflicting requirements, embed the
current authoritative issue text when tracker access is unavailable, verify
that every required check is permitted, and identify product decisions the
supervisor must settle first.

For Claude Code implementation, use the bundled dispatch wrapper. Its default
policy stops the process after five `Read`/`Glob`/`Grep` calls without an edit
and rejects a runtime model switch. Treat either stop as a failed round, not as
a prompt to keep the same process running. When a repair instruction says no
further exploration is needed, enforce `Edit` as the first tool call; do not
rely on prose alone.

Done when: every dispatched feature has a consistent execution contract, all
seven task parts, and an isolated workspace when required.

## 5. Review

For each returned feature, inspect the diff and its verification evidence.
Reuse accepted checks for unchanged code; run missing or affected checks,
starting with deterministic behavior, then targeted UI, then required integration.
Read summaries and failure excerpts before full logs. Repeat a failed command
only after a fix or an identified transient cause.
Executors may propose product decisions; the supervisor decides.

Use the bundled read-only review wrapper for Claude Code reviews. It filters
the stream, permits only declared checks, reports cost and actual models, and
fails if execution switches away from the initialized model. Override its
tool list only with the exact additional read-only checks named in the review
prompt. Never use a raw verbose stream when the wrapper can express the task.

On a failed check or dispatch-policy stop, return the feature to the same
executor once with the concrete failure output and a narrower repair prompt.
If no more discovery is needed, require its first tool to be `Edit`. After two
failed rounds at one level, escalate one level up the ladder; the supervisor
is the top of the ladder and takes the feature over. Re-review the complete
feature diff after repairs, not only the changed fix.

Done when: acceptance checks pass and the diff contains nothing outside the
feature.

## 6. Commit and report

After each reviewed feature, commit — atomic, short imperative message, no
unrelated files. At meaningful milestones, report progress and continue authorized
work unless a user decision is required: changed, verified, remaining risk, provider used,
known quota/spend impact, next feature.

## Self-Review

After finishing, scan the session for orchestrator or provider CLI commands
that misbehaved — needed a retry or extra flag, hit a prompt / pager /
interactive view, blocked, errored, consumed an unexpected quota, or acted
differently than described here. If none did, skip this step.

Otherwise write a few lines: **Worked** (first try), **Didn't** (+ root cause),
**Fix** (one concrete change — name the section, command, or flag). Propose the
`SKILL.md` edit; don't apply it silently.

---
name: orchestrate
description: >
  Supervisor pattern for implementation work: plan and judge with the strong
  model, break work into small end-to-end features, offload execution to the
  cheapest capable executor (subagent or CLI agent), review everything before
  accepting. Use when starting implementation work expected to span multiple
  files or steps, when building a backlog from a spec or PRD, when deciding
  which model or agent should handle a piece of work, or when the user
  mentions delegating, orchestration, subagents, or token cost.
---

# Orchestrate

You are the **supervisor** — the strongest model in the room. The supervisor
never does cheap work and never delegates expensive judgment. Reasoning stays
up, token spend goes down; every step below serves that split. Executors may
run through another provider's CLI or a local model so one provider's quota
does not become the project's bottleneck.

## 1. Assess

Decide whether delegation pays. Delegation has a fixed cost: an **executor**
starts cold and must re-derive context you already hold.

Do it yourself when the work is one file, one behavior, or mostly judgment
(naming, API shape, UI taste). Delegate when it is multi-file, mechanical,
or parallelizable.

For a cross-module task in an unfamiliar codebase, run one cheap read-only
reconnaissance pass first. Require only code anchors, relevant conventions,
and likely checks; feed that concise map to the implementation executor so it
does not repeat broad discovery. Skip this pass when the supervisor already
has those anchors.

When cost or usage limits matter, inventory the available providers before
routing. Record authentication, known remaining quota or spend cap, agentic
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

Never accept unreviewed work. For each returned feature: inspect the diff, run
the acceptance checks (build, tests, runtime verification where relevant).
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

## 6. Report and pause

After each reviewed feature, commit — atomic, short imperative message, no
unrelated files. After 2–3 features, or after any risky or user-facing
change, stop and report: changed, verified, remaining risk, provider used,
known quota/spend impact, next feature.

## Self-Review

After finishing, scan the session for orchestrator or provider CLI commands
that misbehaved — needed a retry or extra flag, hit a prompt / pager /
interactive view, blocked, errored, consumed an unexpected quota, or acted
differently than described here. If none did, skip this step.

Otherwise write a few lines: **Worked** (first try), **Didn't** (+ root cause),
**Fix** (one concrete change — name the section, command, or flag). Propose the
`SKILL.md` edit; don't apply it silently.

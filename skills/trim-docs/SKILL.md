---
name: trim-docs
description: >
  Trim AI context files (skills, prompts, instructions, ADRs) to their minimum
  effective size — cut noise, keep all actionable rules. Use when a document is
  longer than it needs to be, contains rationale where instructions belong, or
  repeats the same rule in multiple forms. Apply KISS, YAGNI, DRY, SRP.
---

# Trim Docs

Reduce a document to its minimum effective size without losing any actionable rule.
The test: *"Can an agent follow exactly the same instructions from the trimmed version?"*
If yes, the cut is safe. If no, keep it.

## What to cut

| Pattern | Example | Principle |
|---|---|---|
| Rationale without instruction | "Agents skim from the top" | KISS |
| Repeated rule in different phrasing | Same point in prose + bold + numbered list | DRY |
| Speculative guidance | Edge case that hasn't occurred yet | YAGNI |
| Procedure that restates the obvious | "Call get_task, then read the result" | KISS |
| Content serving a different task | Setup guide inside a review skill | SRP — move to `references/` or its own doc |

## Never cut — trim, not lobotomize

These survive every pass regardless of length:

- Specific values: timeouts, selectors, cookie names, schema fields, URLs
- "do NOT" rules that prevent a known real mistake
- Security or data-loss constraints
- Trigger conditions in a skill's `description` — tighten wording, keep every "use when" / "do NOT trigger" case
- A one-clause reason that decides edge cases the rule doesn't spell out
- The single sentence that distinguishes this doc from a blank page

ADRs: rationale is the content. Cut only repetition and filler.

## Process

1. **Critique** — list every violation with its pattern from the table; do not rewrite yet
2. **Rewrite** — produce the full trimmed version; add no new rules or content
3. **Diff check** — confirm no "Never cut" item was dropped; report word count before → after

Do NOT write to files until the user approves the rewrite.

For a concrete before/after walkthrough, read `references/example.md`.

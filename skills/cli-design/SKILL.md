---
name: cli-design
description: Design or review the interaction contract of a CLI for humans, scripts, and AI agents — command hierarchy, help, output, errors, exit codes, safety, agent discovery, and bundled agent skills. Use when designing a new CLI or command, extending or auditing an existing CLI's contract, or adding agent support. Not for operating an existing CLI; use that CLI's own skill.
---

# CLI Design

Design the CLI as an interaction contract before choosing framework mechanics. Stay language-independent unless the user asks for a specific stack.

## Terms

- **Machine mode:** any invocation with `--json`, `--ndjson`, or another documented structured renderer. Everything else is **human mode**.
- **Operation class:** `local` (no auth, configuration, or network), `read`, `write`, or `mixed` (a parent whose leaves differ). An unclassified operation counts as `write`.

## Choose the mode

- **New CLI:** define the contract and acceptance criteria before implementation.
- **Extension:** record the existing command tree from the running binary first, then preserve its contracts unless the user authorizes a breaking change. Follow the [per-command change checklist](references/verification.md#per-command-change-checklist).
- **Audit:** compare observed behavior with the contracts and report findings; do not edit unless requested.
- **Implementation:** turn the agreed contract into code using the per-command change checklist, then verify both development and packaged entrypoints.

The installed executable, source checkout, and documentation may be different versions. Record which artifact and version each observation came from. If audiences or authority for breaking changes are unknown, state the assumption in the deliverable and stop before implementing.

## Build the contract

1. Identify audiences and invocation modes: interactive human, script, AI agent.
2. Map the command tree: per command, operation class, arguments, local and inherited options, auth/configuration requirements, output modes, error codes, pagination, and destructive effects.
3. Define one semantic result and error model; human, JSON, and NDJSON output render it. Generate help, completion, discovery, and reference docs from one command metadata source.
4. Apply [the interaction contract](references/interaction-contract.md) to grammar, help, output, streams, errors, pagination, safety, and accessibility.
5. When scripts or agents are in scope, apply [the agent interface](references/agent-interface.md). When the CLI ships or installs an agent skill, also apply [skill distribution](references/skill-distribution.md).
6. Apply [the verification matrix](references/verification.md): in design mode derive acceptance criteria from it; in audit or implementation mode run it. Account for every relevant cell before finishing.

Derive required flags from the operation class ([table](references/interaction-contract.md#safety-and-side-effects)); add any other flag only when a named workflow needs it and its whole scope can support it. Model renderings on [examples](references/examples.md).

## Non-negotiable invariants

- `--help`, version, completion, and discovery are `local`: no authentication, configuration, network, pager, editor, or prompt.
- A bare root or parent with no independent action prints relevant help on stdout and exits `0`.
- Success exits `0`; failing the requested operation exits non-zero. A stable symbolic error code is the primary classifier; callers never parse messages.
- Invalid syntax exits non-zero. Human mode writes a specific diagnostic plus the smallest relevant help to stderr. Machine mode writes one structured error envelope to stderr, may include bounded remediation fields (`hints`, `allowed_values`, `usage`), and leaves stdout empty.
- Successful payloads go to stdout; diagnostics, warnings, progress, and notices go to stderr. Only a documented partial-result contract returns data on stdout with a non-zero exit.
- Every data-returning command and every write supports machine mode. Machine output contains no ANSI, spinner frames, terminal tables, prompts, or prose.
- `--json` changes representation, never operation semantics, field meaning, pagination, or safety.
- Lists expose completeness. Limits, truncation, cursors, scan caps, and partial failures are never silent.
- No agent-relevant path waits on a prompt, pager, editor, or browser. A destructive or irreversible action without explicit confirmation fails fast when not interactive.
- Input is validated completely before the first side effect or network call.
- Error codes, exit codes, identifiers, timestamps, nullability, ordering, and schemas are documented at the level consumers rely on.
- Secrets arrive through protected environment, configuration, or stdin — never argv — and never appear in output, diagnostics, logs, or examples.

## Deliverable

- **New CLI / Extension:** a specification: scope, audiences, assumptions, inspected artifact/version; command tree with operation classes; shared help, output, stream, error, exit, pagination, and safety contracts; human and machine renderings of the same data; agent discovery and skill design when applicable; acceptance criteria; compatibility and migration notes.
- **Audit:** a findings table — invariant or matrix cell, evidence with artifact and version, severity, proposed contract — followed by the cells not verified.
- **Implementation:** changed contracts, matrix cells passing in both source and packaged entrypoint, and migration notes.

Grade each item by impact on the caller of that command: **required** = blocker (a script or agent cannot proceed safely or correctly), **recommended** = friction (retries, wasted tokens, brittle parsing), **optional** = optimization. Show command and output shapes, never framework code.

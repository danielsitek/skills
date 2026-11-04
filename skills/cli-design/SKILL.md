---
name: cli-design
description: Design or review language-independent CLI interaction contracts for humans, scripts, and AI agents. Use when defining command hierarchy, contextual help, stdout and stderr behavior, exit and error contracts, JSON or NDJSON output, non-interactive safety, capability discovery, shell completion, or bundled agent skills. Do not use merely to operate an existing CLI.
---

# CLI Design

Design the CLI as an interaction contract before choosing framework-specific mechanics. Keep the recommendations language-independent unless the user explicitly asks for implementation guidance in a particular stack.

## Choose the mode

- **New CLI:** define the contract and acceptance criteria before implementation.
- **Extension:** inspect the existing command tree and preserve its established contracts unless the user authorizes a breaking change.
- **Audit:** compare observed behavior with the contracts below and report prioritized findings; do not edit unless requested.
- **Implementation:** turn the agreed contract into code, then verify both development and packaged entrypoints.

For an existing CLI, treat its installed executable, source checkout, and documentation as potentially different versions. Record which artifact and version each observation came from.

## Build the contract

1. Identify the audiences and invocation modes: interactive human, redirected or scripted use, and AI agent automation.
2. Map the command tree. For each command, record its operation class (`local`, `read`, `write`, or `mixed`), arguments, local and inherited options, authentication/configuration requirements, output modes, possible exit codes, interactivity, pagination, and destructive effects.
3. Define one semantic result and error model. Human, JSON, and streaming output are renderers of that model, not separate behaviors.
4. Apply [the interaction contract](references/interaction-contract.md) to command hierarchy, help, streams, output, errors, safety, and accessibility.
5. When scripts or agents are in scope, apply [the agent interface](references/agent-interface.md) to non-interactive operation, capability discovery, and bundled skills.
6. For an audit or implementation, apply [the verification matrix](references/verification.md). Account for every relevant command level and failure class before declaring the work complete.

Prefer a small consistent surface over adding every potentially useful flag. Recommend `--json`, `--ndjson`, `--quiet`, `--ids-only`, `--fields`, `--jq`, `--template`, `--all`, `--cursor`, `--dry-run`, or `--yes` only when they solve a real workflow and can be supported consistently.

## Non-negotiable invariants

- `--help`, version reporting, completion generation, and capability discovery are local operations: no authentication, configuration, network, pager, editor, or prompt.
- A bare root or parent command that has no independent action returns relevant help or a safe overview on stdout with exit `0`.
- Invalid syntax returns a non-zero usage exit. Human mode writes a specific diagnostic and relevant contextual help to stderr; machine mode writes one structured error without prose or help text.
- Successful payloads go to stdout. Diagnostics, warnings, update notices, and progress go to stderr. A documented partial-result contract may return useful data on stdout with a distinct non-zero exit.
- Machine output contains no ANSI sequences, spinner frames, terminal tables, prompts, or incidental prose.
- `--json` changes representation, not operation semantics, field meaning, pagination, or safety.
- Lists expose whether results are complete. Limits, truncation, cursors, scan caps, and partial failures are never silent.
- Destructive or difficult-to-reverse actions have an explicit non-interactive contract. Automation never waits on an unannounced prompt.
- Error codes, exit codes, identifiers, timestamps, nullability, ordering guarantees, and output schemas are documented at the level consumers can rely on.
- Secrets are accepted through protected environment/configuration or stdin mechanisms, never echoed in diagnostics or placed in examples as command-line arguments.

## Deliverable

Return a concrete, implementation-independent specification with:

1. Scope, audiences, assumptions, and the inspected artifact/version when applicable.
2. Command tree and per-command operation classification.
3. Shared help, output, stream, error, exit, pagination, and safety contracts.
4. Human presentation and machine representation of the same data.
5. Agent discovery and bundled-skill design when applicable.
6. Acceptance criteria derived from the verification matrix.
7. Compatibility or migration notes for changes to an existing CLI.

Label recommendations as **required**, **recommended**, or **optional**. Show representative command and output shapes where they remove ambiguity, but do not turn examples into a framework-specific implementation.

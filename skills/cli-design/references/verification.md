# Verification matrix

Use for acceptance criteria, audits, and implementations. Verify observable contracts, not framework internals or incidental wording.

## Establish the target

Record the executable path and version, source revision, development and packaged entrypoints, relevant configuration and environment without secret values, and whether stdout and stderr are TTYs. If installed and source versions differ, test and label them separately; never claim a source fix is present in the installed binary.

## Command-tree coverage

Enumerate command paths from parser metadata, completion, or discovery. Cover every parent, not only root and leaves; parameterize tests over all registered parents.

| Case | Human expectation | Machine expectation |
| --- | --- | --- |
| Empty root | Root help/overview, exit `0` | Same, unless a structured root mode is documented |
| Empty parent | Parent help, exit `0` | Structured help/discovery if supported |
| Explicit help | Contextual help, exit `0` | Help stays local; structured data unpolluted |
| Missing argument | Diagnostic plus leaf help, usage exit | One `invalid_usage` envelope on stderr |
| Unknown subcommand | Diagnostic plus parent help, usage exit | One `invalid_usage` envelope on stderr |
| Success | Human renderer on stdout | Parseable documented schema on stdout |
| Empty success | Clear empty state | Stable empty collection/object |
| Domain failure | Actionable stderr diagnostic | Stable error code and envelope |
| Unconfirmed destructive | Fails fast when not interactive; no change | `confirmation_required`-style error; no change |
| Partial write | Completed/failed stages, distinct exit | Parseable partial result, distinct exit |
| Async with `--wait` | Final result or documented timeout outcome | Same, parseable, with job ID |

## Output and stream assertions

- Capture stdout, stderr, and exit code independently. Parse JSON and NDJSON; never match them as text.
- Assert one JSON value per documented unit, newline-terminated, with no ANSI, spinner frames, table borders, prompts, or help prose.
- Assert machine errors land on stderr with stdout empty, and input errors carry the valid set or a correct invocation.
- Every data-returning command and every write has a machine renderer; record a human-only command as a finding.
- Every status or enum value has a human rendering; a new value without one fails a test.
- Simulate TTY and non-TTY independently for stdout and stderr. Exercise `NO_COLOR`, accessible, quiet, progress, and debug modes the CLI claims.
- Verify errors and verbose output redact tokens, authorization headers, credentials, and sensitive configuration.

Assert semantic sections, schemas, and stream placement. Reserve golden snapshots for presentation that is itself the contract.

## Data and pagination assertions

- Identifiers are strings and stable across renderers.
- Dates, timezones, nulls, omitted fields, and ordering match the documented schema.
- Test zero, one, default-limit, limit-plus-one, and multi-page results.
- Verify `has_more`, cursor/offset, scanned and returned counts, truncation signals, and that an NDJSON trailing metadata record appears only when the result is incomplete.
- Fail a later page and verify an incomplete set is never presented as complete.
- `--all` respects its cap and reports cap exhaustion.
- Field selection or projection does not alter filtering, pagination, or errors.

## Safety assertions

- Run every agent-relevant command, including `--wait` paths, with stdin closed and a timeout. A hang or prompt is a blocker.
- Run reads against dependencies that fail on any mutation. Run `local` commands against dependencies that fail on authentication, configuration, network, stdin, or filesystem writes.
- Invalid or conflicting input makes no network call and no write.
- Unconfirmed destructive commands fail fast when not interactive, in both human and machine mode.
- `--dry-run` identifies the same targets as execution, writes nothing, and reports a preview.
- Under a read-only credential or mode, every non-`read` command is blocked, including newly added ones.
- A repeated idempotent write reports `unchanged` or `already_exists`. Test retry at every failure boundary of a multi-stage write; partial completion reports exactly what changed.
- Cancellation never prints success and reports potentially completed effects.
- Skill install, update, and uninstall run against temporary roots; unrelated files survive.

## Discovery and documentation

- Discovery paths match the registered command tree with no missing or duplicate paths. Arguments, options, inheritance, operation class, requirements, and exit categories match parser behavior.
- Command and flag names pass the naming policy.
- Ordering is deterministic and the schema is versioned.
- Help, completion, discovery, and version work offline and before login.
- Examples execute or parse as documented without real credentials.
- Every command path and flag named in the bundled skill exists in the packaged CLI.

## Per-command change checklist

Adding or changing a command touches each item below. Update it or record why it does not apply.

1. Parser registration and one-line description.
2. Help text and examples.
3. Human and machine renderers.
4. Error codes and remediation hints.
5. Operation class and read-only permission classification.
6. Discovery metadata (generated; verify it).
7. Test doubles for the remote service.
8. Tests: success, invalid input, machine output, and for writes a dry run asserting no mutation.
9. Operator skill content when the command is agent-relevant.
10. Changelog and compatibility notes.

## Completion criterion

An audit is complete when every relevant cell is verified, identified as unsupported, or recorded as a finding with evidence. An implementation is complete when source tests and the packaged executable both satisfy the agreed cells and compatibility changes are documented.

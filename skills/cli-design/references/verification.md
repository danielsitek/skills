# Verification matrix

Use this reference for audits and implementations. Verify observable contracts, not framework internals or exact incidental wording.

## Establish the target

Record:

- executable path and version,
- source revision when source is available,
- development and packaged entrypoints,
- relevant configuration and environment without secret values,
- whether stdout and stderr are attached to a TTY.

If installed and source versions differ, test and label them separately. Do not claim a source fix is present in the installed binary.

## Command-tree coverage

Enumerate command paths from parser metadata, completion, capabilities, or help. Account for every parent command, not only root and leaf commands.

For each relevant root, parent, and leaf level, cover:

| Case | Human expectation | Machine expectation |
| --- | --- | --- |
| Empty root | Root help/overview, exit `0` | Same safe behavior unless a structured root mode is documented |
| Empty parent | Parent help, exit `0` | Structured help/capability behavior if supported |
| Explicit help | Contextual help, exit `0` | Help remains local; structured data is not polluted |
| Missing argument | Specific diagnostic plus leaf help, usage exit | One structured `invalid_usage` error |
| Unknown subcommand | Specific diagnostic plus parent help, usage exit | One structured `invalid_usage` error |
| Success | Human renderer on stdout | Parseable documented schema on stdout |
| Empty success | Clear empty state | Stable empty collection/object |
| Domain failure | Actionable stderr diagnostic | Stable error code/envelope |
| Partial write | Completed/failed stages and distinct exit | Parseable partial result and distinct exit |

Parameterize these tests over all registered parent commands. Testing only root help leaves the most common hierarchy regression undetected.

## Output and stream assertions

- Capture stdout, stderr, and exit code independently.
- Parse JSON/NDJSON rather than matching it as arbitrary text.
- Assert one JSON value per documented unit and a terminating newline.
- Assert no ANSI, spinner frames, table borders, prompts, or help prose in machine output.
- Assert successful machine commands keep stdout pure and stderr contains only documented warnings, diagnostics, or requested progress events.
- Redirect stdout and confirm it remains complete and usable.
- Simulate TTY and non-TTY streams independently when the renderer adapts.
- Exercise `NO_COLOR`, accessibility, quiet, progress, and debug modes that the CLI claims to support.
- Verify errors and verbose output redact tokens, authorization headers, credentials, and sensitive configuration.

Avoid brittle full snapshots for wrapping, whitespace, and color. Assert the semantic sections, local command context, stable schemas, and stream placement. Use focused golden tests only when presentation itself is the contract.

## Data and pagination assertions

- Verify identifiers remain strings and stable across renderers.
- Verify dates, timezones, nulls, omitted fields, and ordering against the documented schema.
- Test zero, one, default-limit, limit-plus-one, and multi-page results.
- Verify `has_more`, cursor/offset, scanned count, returned count, and truncation signals where supported.
- Interrupt or fail a later page and verify the command does not present an incomplete set as complete.
- Verify `--all` respects its documented safety cap and exposes cap exhaustion.
- Verify field selection does not alter filtering, pagination, or error semantics.

## Safety assertions

- Run reads against dependencies that fail if any mutation is attempted.
- Run local discovery against dependencies that fail if authentication, configuration, network, stdin, or mutable filesystem access is attempted.
- Verify destructive commands fail fast without explicit confirmation in non-interactive mode.
- Verify `--dry-run` identifies the same targets as execution without performing writes.
- Test retry and idempotency behavior at every failure boundary of a multi-stage write.
- Verify partial completion reports exactly what changed and what remains.
- Verify cancellation does not print success and documents potentially completed effects.
- Test install/update/uninstall against temporary roots and confirm unrelated files survive.

## Capabilities and documentation

- Compare capability paths with the actual registered command tree; there are no missing or duplicate paths.
- Compare arguments, options, inheritance, operation class, requirements, output modes, and exit codes with parser behavior.
- Verify deterministic ordering and schema versioning.
- Confirm `--help`, completion, capabilities, and version work offline and before login.
- Check that examples execute or parse as documented without exposing real credentials.
- Check the agent skill against the packaged CLI version, not only the source tree.

## Completion criterion

An audit is complete when every relevant matrix cell is either verified, identified as unsupported, or recorded as a finding with evidence. An implementation is complete when the source tests and the packaged executable both satisfy the agreed cells, and compatibility changes are documented.

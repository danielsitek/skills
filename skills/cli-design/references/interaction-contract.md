# Interaction contract

Detail behind the SKILL.md invariants for grammar, help, output, streams, errors, pagination, safety, and accessibility. Define the semantic contract first; render it for people and machines.

## Command grammar

- Use one grammar for substantial surfaces, such as `tool <noun> <verb>`. Keep the root to stable domains; group related operations under a parent.
- Use the same verb for the same operation across resources: `list`, `get`, `create`, `update`, `delete`.
- Use one name per concept across all commands (always `--limit`, never also `--max`). Record banned synonyms in a naming policy checked against command metadata.
- `--yes` bypasses confirmation; `--force` overrides overwrite or safety protection. One flag never means both.
- Accept `-` for stdin/stdout wherever a file path is accepted.
- Alias only frequent human shortcuts. Help, docs, discovery, and agent guidance use the canonical spelling.
- Human shorthand (natural language, positional guesses) may coexist, but precise behavior always has an explicit flag route.
- Accept stable IDs and canonical URLs. Treat names as convenience resolution and report ambiguity instead of choosing silently. Where name lookup is impossible, accept IDs only and reject plain text with a specific error.
- Inherited options behave the same across the subtree. Document their origin and whether they may appear before or after subcommands.

## Help and discovery

Every command level owns its help.

- Root: purpose, usage, global options, command groups, examples, how to reach deeper help.
- Parent: group purpose, subcommands, inherited options, examples that distinguish neighbors.
- Leaf: argument meaning, required and mutually exclusive options, defaults, side effects, accepted identifiers, examples, exit behavior.
- Every command has a one-line description that distinguishes it from its siblings; agents choose commands by it.
- A missing argument shows leaf help; an unknown subcommand shows parent help. Both exit with the usage code.
- `help <path>` and `<path> --help` resolve to the same context.
- Show the smallest help that lets the caller fix the invocation.
- An implicit default subcommand turns a bare parent into a missing-argument case and shadows resources named like subcommands. Adopt one only deliberately, document it, and teach agents the explicit form.
- Completion is generated from command metadata and does no remote reads unless documented.

## Human and machine renderers

| Concern | Human mode | Machine mode |
| --- | --- | --- |
| Layout | Headings, whitespace, concise tables or blocks | One documented schema |
| Color | TTY-aware enhancement | Never emitted |
| Empty result | Clear sentence | Empty array/object with stable shape |
| Dates | Readable when helpful; preserve exact value when needed | ISO 8601 with defined timezone semantics |
| Identifiers | May be visually de-emphasized | Always present, as strings |
| Progress | TTY spinner or concise status on stderr | Disabled, or explicit NDJSON progress on stderr/file |
| Warnings | Actionable stderr text | Structured diagnostic on stderr |
| Detail level | Useful defaults with opt-in detail | Documented default projection; explicit full/field selection if supported |

Render human output from structured domain data, never by decorating or parsing pre-rendered strings.

### JSON and NDJSON

- Emit one JSON value per finite invocation, newline-terminated, with a stable top-level shape. An envelope such as `{"data": ..., "meta": ...}` helps when pagination and version metadata recur.
- Use NDJSON for unbounded or incremental results: one complete value per line. When the result is incomplete, end with a distinguishable metadata record carrying the cursor, such as `{"_meta": true, "next_cursor": "..."}`.
- Default output may be a documented essential-field projection with an explicit flag (such as `--full`) for the whole record. The projection is part of the contract.
- Field selection, if offered, lists valid fields locally and changes only the selected data, never errors or pagination.
- A write that returns no entity still returns a structured result: outcome, affected IDs, and URL where available. Never wrap captured prose in JSON.
- Add fields freely; version the schema before changing a field's meaning or type.
- Identifiers are strings, even when numeric.
- Distinguish absent, unknown, and `null` where the domain does.
- State ordering guarantees; if order is unspecified, consumers must not need it.

## Streams

- Redirected stdout stays complete and usable without terminal detection.
- In machine mode, a successful run leaves stderr empty unless a documented warning or requested progress event occurs.
- A partial operation returns a structured result on stdout listing completed and failed stages, a distinct non-zero exit, and a concise stderr diagnostic. Consumers distinguish partial from total failure without parsing prose.

## Errors and exit codes

One error taxonomy serves all renderers. Each error carries a stable symbolic code, a safe actionable message, `retryable`, an exit category, and structured details where they help remediation. The underlying cause goes to debug output only. See [examples](examples.md) for the envelope.

- Input errors name the invalid value, the valid set (capped when large), and one correct invocation, in `allowed_values`, `usage`, or `hints`.
- `0` means success. `2` for invalid usage is recommended. Add further distinct exits (authentication, not found, rate limit, partial completion, internal) only when shell callers branch on them; document each command's subset.
- Map expected domain failures before the catch-all internal error.
- Stack traces appear only in an explicit debug mode, still redacted.
- If retrying may duplicate a write, say so and offer an idempotency key where the domain permits.

## Bounded reads and pagination

- List operations have a documented default limit, and a scan limit where remote filtering is incomplete.
- Report returned and scanned counts, a cursor or offset, and `has_more`. When truncated, name the narrowing flag or the exact next-page command — in `meta` in machine mode, on stderr in human mode.
- `--all` is explicit and bounded by a caller-controlled cap; reaching the cap is reported.
- Never label a first page "all", "latest", or "complete" without proof of exhaustion. If a newest-N result needs a full scan, finish it within a visible cap or fail.

## Safety and side effects

A `mixed` parent never conceals whether a leaf writes. Reads never mutate local configuration as a hidden prerequisite.

| Class | Machine result | Preview | Confirmation |
| --- | --- | --- | --- |
| `read` | data; lists add limit, cursor, bounded `--all` | — | — |
| `write` (create, update, reversible archive/close) | entity or outcome with stable IDs; `--quiet` may print the bare ID | `--dry-run` when it can be faithful | none |
| `write`, destructive or irreversible | outcome with affected IDs | `--dry-run` when it can be faithful | `--yes` |
| async submit | job ID, or final result with `--wait` | per underlying class | per underlying class |

- Writes accept the complete intended change before starting; no mid-operation prompts.
- `--dry-run` resolves the same targets as execution, writes nothing, and labels its result as a preview, never success.
- Overwrite, replacement, cascade, and force behavior are explicit.
- A repeated idempotent write reports `unchanged` or `already_exists` with the stable ID — no error, no duplicate. Base idempotency on an explicit or natural key, never on content matching.
- A multi-stage write that fails partway reports every completed stage.
- A read-only credential or mode is default-deny: anything not classified `read` is blocked with a distinct error code.
- Configuration commands identify the winning source without exposing values.

### Async operations

Apply when a command submits work that completes later.

- Without `--wait`, return the job ID immediately. With `--wait`, poll with backoff and jitter up to a caller timeout and return the final result.
- A timeout returns the job ID and last status as a distinct, documented outcome. Interrupting stops waiting, not the job; cancellation is a separate explicit command.
- Document terminal states; a failed terminal state maps to the normal error envelope.
- `jobs get` and `jobs list` are `read`. A retried submit with the same idempotency key finds the in-flight job, preferably by server lookup rather than a local ledger.

## Terminal adaptation and accessibility

- Detect TTY independently for stdout and stderr. Use color and spinners only on a TTY in human mode; honor `NO_COLOR`.
- Never carry status by color alone. In accessible mode, replace bars and decorative glyphs with their value.
- At 80 columns, tables fit or fall back to blocks.
- Open a browser, pager, or editor only through explicit opt-in.

## Supporting local commands

- `completion <shell>` for interactive CLIs.
- `doctor` when authentication, configuration, or connectivity failures are a common support issue. It reports the winning configuration source without secret values.
- Discovery: see [agent-interface.md](agent-interface.md#capability-discovery).

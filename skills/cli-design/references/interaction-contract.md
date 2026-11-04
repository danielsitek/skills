# Interaction contract

Use this reference when designing or reviewing command hierarchy, help, output, errors, or safety. Define the semantic contract first; render it differently for people and machines.

## Command grammar

- Organize substantial surfaces as `tool <noun> <verb>` or another single, consistent grammar. Optimize names for discovery, not minimum character count.
- Keep the root focused on stable domains. Put related operations under a parent command instead of accumulating unrelated top-level verbs.
- Use the same verb for the same operation across resource families: for example `list`, `get`, `create`, `update`, and `delete`.
- Give aliases only to frequent human shortcuts. Keep one canonical spelling in help, documentation, capabilities, and agent guidance.
- Prefer explicit structured flags for automation. Natural-language shorthand may coexist as a human convenience, but it must not be the only route to precise behavior.
- Accept stable IDs and canonical URLs where useful. Treat fuzzy names as convenience resolution and expose ambiguity rather than choosing silently.
- Keep inherited options consistent across the whole subtree. Document where an option originates and whether it may appear before or after subcommands.

## Help and discovery

Every command level owns its help.

- Root help states purpose, usage, global options, command groups, representative examples, and how to reach deeper help.
- Parent help states the group's purpose, its subcommands, inherited options, and examples that distinguish neighboring operations.
- Leaf help states argument meaning, required and mutually exclusive options, defaults, side effects, accepted identifiers, examples, and relevant exit behavior.
- A bare root or parent with no independent action behaves like its help and exits `0`.
- A missing argument shows leaf help; an unknown subcommand shows parent help. Both retain the non-zero usage exit.
- `help <path>` and `<path> --help` should resolve to the same command context.
- Keep help deterministic and local. It must work before login and when the remote service is unavailable.
- Generate shell completion from the same command metadata when practical. Completion must not trigger remote reads unless explicitly documented.

Do not dump the entire manual after every error. Show the smallest context that lets the user correct the invocation.

## Human and machine renderers

| Concern | Human mode | Machine mode |
| --- | --- | --- |
| Layout | Headings, whitespace, concise tables or blocks | One documented schema |
| Color | TTY-aware enhancement | Never emitted |
| Empty result | Clear sentence | Empty array/object with stable shape |
| Dates | Readable when helpful; preserve exact value when needed | Stable ISO 8601 value and timezone semantics |
| Identifiers | May be visually de-emphasized | Always available as strings |
| Progress | TTY spinner or concise status on stderr | Disabled, or explicit JSONL progress on stderr/file |
| Warnings | Actionable stderr text | Structured diagnostic on stderr |
| Detail level | Useful defaults with opt-in detail | Stable documented default; explicit field selection if supported |

Render human output from structured domain data rather than parsing or decorating pre-rendered strings. This keeps presentation changes from altering machine contracts.

### JSON

- Emit exactly one JSON value for a finite invocation and terminate it with a newline.
- Use a stable top-level shape. An envelope such as `{"data": ..., "meta": ...}` is useful when pagination and version metadata recur across commands.
- Use `--ndjson` or another explicitly named JSONL mode for unbounded or incremental results. Emit one complete JSON value per line.
- Keep property meaning and types stable. Additive fields are safer than reinterpretation; version a schema before making incompatible changes.
- Represent identifiers as strings even when currently numeric.
- Distinguish absent, unknown, and explicit `null` when the domain distinguishes them.
- State ordering guarantees. If order is unspecified, consumers must not need it.
- A field-selection feature should report valid fields through help or local discovery rather than trial-and-error against the remote service.

### Quiet and selection modes

Add specialized modes only when their contract is simple:

- `--quiet`: suppresses success prose; a create operation may still emit the created stable ID.
- `--ids-only`: one ID per line, with no header or empty-state prose.
- `--fields`: changes the selected data, not error or pagination semantics.
- `--jq` or `--template`: transforms already structured output; document interaction with `--json`.

Define mutual exclusions instead of producing ambiguous mixtures.

## Streams

- stdout carries the requested result.
- stderr carries diagnostics, warnings, progress, deprecation notices, and update notices.
- A successful machine invocation keeps stdout pure. Stderr is empty unless a documented warning, diagnostic, or requested progress event occurs.
- Redirected stdout remains usable without special terminal detection.
- Never write a secret, authorization header, raw credential, or sensitive configuration value to either stream.

A partial operation needs an explicit contract. Prefer a structured result describing completed and failed stages on stdout, a distinct non-zero exit, and a concise diagnostic on stderr. Consumers must be able to distinguish partial completion from total failure without parsing prose.

## Errors and exit codes

Use one internal error taxonomy across renderers. Each error carries:

- a stable symbolic code,
- a safe actionable message,
- structured details where they help remediation,
- whether retry may succeed,
- an exit category,
- the underlying cause for logs without exposing it by default.

Human errors may explain the next action. Machine errors use one documented envelope, for example:

```json
{"error":{"code":"invalid_usage","message":"Missing required project ID","retryable":false}}
```

Keep exit codes few and stable. `0` means success; common conventions favor `2` for invalid usage. Add distinct categories only when callers can make a useful decision, such as authentication/authorization, remote or not-found failure, rate limiting/retry exhaustion, partial completion, and unexpected internal failure. Document command-specific subsets.

- Never return `0` after failing the requested operation.
- Never require callers to parse a localized message to classify an error.
- Map expected domain failures before the catch-all internal error.
- Hide stack traces by default; expose them only through an explicit debug mode that still redacts secrets.
- If retrying may duplicate a write, say so and provide an idempotency mechanism where the domain permits it.

## Bounded reads and pagination

- Give list operations a documented default result limit and scan limit where remote filtering is incomplete.
- Distinguish items returned from items scanned.
- Return a cursor/offset and `has_more` or an equivalent completeness signal.
- Make `--all` explicit and bounded by a caller-controlled cap when the source may be large.
- Do not label the first page as "all", "latest", or "complete" unless source exhaustion was proven.
- If a requested newest-N result requires scanning the full source, either complete that scan within a visible cap or fail without returning a misleading subset.

## Safety and side effects

Classify every command as `local`, `read`, `write`, or `mixed`. A `mixed` parent must not conceal whether a specific leaf writes.

- Read commands do not mutate local configuration as a hidden prerequisite.
- Writes accept the complete intended change before starting; avoid mid-operation prompting.
- Destructive commands support an explicit confirmation flag for automation. A non-interactive environment fails fast when confirmation is missing.
- Offer `--dry-run` when the preview can faithfully show targets and material effects.
- Make overwrite, replacement, cascade, and force behavior explicit.
- Define idempotency for create, update, retry, and uninstall paths.
- Report every completed stage when a multi-stage write partially fails.
- Configuration commands identify the winning source without exposing sensitive values.

## Terminal adaptation and accessibility

- Detect TTY independently for stdout and stderr.
- Disable color when redirected and honor a standard no-color mechanism.
- Never make color the only carrier of status; add text, symbols, or accessible labels.
- Keep tables readable at narrow widths or fall back to blocks.
- Disable spinners in non-TTY mode and when structured output is selected.
- Avoid mandatory interactive selectors. Provide flags or stdin alternatives for every agent-relevant workflow.
- Avoid automatic pagers and editors in scripted paths; provide explicit opt-in commands for opening a browser, pager, or editor.

## Supporting local commands

Consider these when the product justifies them:

- `completion <shell>` for shell completion.
- `doctor` for local authentication, configuration, connectivity, and dependency diagnostics.
- `config show --sources` for layered configuration provenance.
- `version --json` when automation needs build metadata beyond a stable text version.
- `capabilities --json` for machine-readable discovery; see [agent-interface.md](agent-interface.md).

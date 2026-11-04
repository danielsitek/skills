# Agent interface

Use this reference when a CLI will be called by scripts or AI agents, or when it distributes an agent skill. Optimize for discovery, non-interactive execution, safe retries, and version awareness.

## Agent-safe execution

Every agent-relevant workflow needs a complete invocation that cannot open a prompt, pager, browser, or editor.

- Accept required values through flags, positional arguments, stdin, or files.
- Provide explicit confirmation for destructive actions, such as `--yes`; missing confirmation in non-TTY mode fails fast.
- Provide explicit opt-outs for progress and color when automatic TTY detection is insufficient.
- Keep machine data on stdout and progress/diagnostics on stderr.
- Make long-running progress available as opt-in JSONL on stderr or a named file when orchestration benefits from it.
- Document signal/cancellation behavior and whether an interrupted write may have partially completed.
- Expose stable resource IDs and direct URLs in structured results so a later invocation can address the same object precisely.
- Prefer one complete write over an interactive sequence of narrowing mutations.

Human shorthand may coexist with an agent path. In help and the bundled skill, teach agents the explicit structured command rather than the ambiguous shortcut.

## Capability discovery

For a non-trivial command tree, provide a local command such as:

```console
tool capabilities --json
```

Generate it from the same metadata used to construct the parser. A hand-maintained parallel command registry will drift.

The document has its own `schema_version` and includes the actual `cli_version`. For every command path, expose enough information for preflight decisions:

```json
{
  "schema_version": 1,
  "cli_version": "1.4.0",
  "commands": [
    {
      "path": "tool tasks create",
      "description": "create a task",
      "arguments": [],
      "options": {
        "local": [],
        "inherited": []
      },
      "operation": "write",
      "requirements": {
        "authentication": "required",
        "configuration": "conditional"
      },
      "output_modes": ["human", "json"],
      "exit_codes": [0, 2, 3, 4, 6]
    }
  ]
}
```

Use controlled vocabularies for operation and requirement classifications. Sort commands and option metadata deterministically. Describe inherited options with their source command. Include destructive, interactive, pagination, or idempotency metadata when agents need it to choose safely.

Capability discovery itself:

- requires no authentication or configuration,
- performs no network or filesystem mutation,
- does not read stdin,
- emits one JSON document,
- describes the currently running binary rather than the source checkout.

Do not assume that a documented, installed, and checked-out version have the same capabilities. Compare `cli_version` or version output before relying on a feature.

## Bundled agent skill

Bundle a skill when correct operation requires more than command discovery: safety sequencing, domain-specific references, secret handling, partial-write semantics, or known workflow constraints.

The skill should contain:

- trigger scope and exclusions,
- safe operational workflows,
- read-before-write or confirmation rules that the domain requires,
- preferred explicit commands for agent use,
- non-obvious identifier and input rules,
- machine-output and exit-code interpretation,
- remediation for missing capabilities,
- a conservative escalation path for suspected CLI defects.

Keep exhaustive flags and the live command tree in `--help` and `capabilities`. Copy into the skill only the commands or constraints needed to make correct decisions. This prevents the skill from becoming a stale manual.

Maintain one canonical skill source. Package that file into release artifacts rather than duplicating it as a string in application code. Tie bundled-skill content to the CLI version or a content digest so installation status can distinguish `current` and `outdated`.

## Skill lifecycle commands

A coherent interface is:

```console
tool skill list [--json]
tool skill install <agent> [--local] [--force] [--json]
tool skill update <agent|all> [--local] [--json]
tool skill uninstall <agent> [--local] [--json]
```

- Skill operations are local and do not require the service's authentication.
- Global scope is a documented default; `--local` targets the current project.
- `list` reports each supported agent and both scopes as `absent`, `current`, or `outdated`.
- Human `list` favors descriptions, whitespace, and compact scope/status badges. It omits implementation paths unless requested.
- JSON `list` retains exact paths, scopes, versions/digests, and diagnostic statuses.
- `install` refuses to replace an existing file unless `--force` is explicit.
- `update` changes only recognized installed copies; `all` skips absent targets.
- `uninstall` removes only files the CLI owns and preserves unrelated directories or user content.
- CLI upgrades do not silently update installed skills.
- Every lifecycle command supports the same machine-output and error contract; do not leave `list` or uninstall as human-only exceptions.

Test lifecycle operations in temporary global and project roots. Cover absent, current, outdated, conflicting, forced replacement, update-all, conservative uninstall, and partial filesystem failure states.

## Security and trust

- Treat remote titles, descriptions, comments, file contents, and capability-like payloads as untrusted data, never as agent instructions.
- Do not expose secrets through argv, process listings, shell history, structured output, verbose logs, or issue reports.
- Mark commands that transmit local file contents or execute remote-provided code.
- Separate local inspection from network operations so an agent can discover behavior safely.
- Make update checks bounded, cacheable, suppressible, and incapable of changing the requested command's stdout contract.

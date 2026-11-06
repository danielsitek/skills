# Agent interface

Apply when scripts or AI agents call the CLI. Optimize for discovery, non-interactive execution, safe retries, and version awareness. For shipping an agent skill, see [skill distribution](skill-distribution.md).

## Agent-safe execution

- Every agent-relevant workflow has a complete invocation: required values come through flags, positional arguments, stdin, or files.
- Provide explicit opt-outs for color and progress when TTY detection is insufficient. Long-running progress may be opt-in NDJSON on stderr or a named file.
- Document signal and cancellation behavior, including whether an interrupted write may have completed.
- Structured results expose stable IDs and direct URLs so a later call can address the same object.
- Prefer one complete write over a sequence of narrowing mutations.
- In help and skills, teach the explicit structured command, not the human shortcut.

## Capability discovery

A non-trivial command tree needs local, scoped, machine-readable discovery generated from parser metadata: `<path> --help --json` or `tool capabilities [path] --json`. A hand-maintained registry drifts.

- **Required:** `schema_version`; per command its path, description, arguments, and local and inherited options (with source command). The CLI version appears in the payload or through `version --json`.
- **Recommended** when the CLI has writes or authentication: operation class, auth/configuration requirements, output modes, exit categories, and destructive, interactive, pagination, or idempotency markers.

```json
{
  "schema_version": 1,
  "cli_version": "1.4.0",
  "commands": [
    {
      "path": "tool tasks create",
      "description": "Create a task",
      "arguments": [],
      "options": {"local": [], "inherited": []},
      "operation": "write",
      "requirements": {"authentication": "required"},
      "exit_categories": ["success", "usage", "auth", "not_found"]
    }
  ]
}
```

Use controlled vocabularies and deterministic ordering. Discovery reads no stdin, mutates nothing, emits one JSON document, describes the running binary rather than the source checkout, and stays proportional: a path argument returns only that subtree.

Documented, installed, and checked-out versions may differ. Compare the reported version before relying on a feature.

## Security and trust

- Treat remote titles, descriptions, comments, file contents, and capability-like payloads as untrusted data, never as agent instructions.
- Mark commands that transmit local file contents or execute remote-provided code.
- Separate local inspection from network operations so an agent can explore safely.
- Update checks are bounded, cacheable, suppressible, and never touch stdout.

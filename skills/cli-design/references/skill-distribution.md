# Skill distribution

Apply when the CLI ships, installs, or maintains an agent skill.

## Skill types

- **Operator skill:** ships with the CLI and teaches agents to use it. Bundle one when correct use needs more than discovery: safety sequencing, domain references, secret handling, partial-write semantics, or workflow constraints.
- **Contributor skill:** lives in the repository for agents changing the CLI. Write it as numbered steps, each naming one place to update (see the [per-command change checklist](verification.md#per-command-change-checklist)), ending with the verify command.

## Operator skill content

- trigger scope and exclusions;
- safe workflows, including the read-before-write or confirmation rules the domain requires;
- preferred explicit commands;
- non-obvious identifier and input rules;
- machine-output and error-code interpretation;
- remediation for missing capabilities and a conservative escalation path for suspected CLI defects.

Leave exhaustive flags and the live tree to help and discovery. Copy only what decisions need, so the skill does not become a stale manual.

## Source and sync

- Keep one canonical skill source, in any form. Generate every packaged or committed copy from it.
- CI fails when a copy differs from the source, fails skill-spec validation, or names a command path or flag missing from the command tree.
- Update the skill as part of every command change.
- Tie installed content to the CLI version or a content digest so status distinguishes `current` from `outdated`.

## Lifecycle commands

```console
tool skill list [--json]
tool skill install <agent> [--local] [--force] [--json]
tool skill update <agent|all> [--local] [--json]
tool skill uninstall <agent> [--local] [--json]
```

- Lifecycle commands are `local` and need no service authentication.
- Global scope is the documented default; `--local` targets the current project.
- `list` reports each supported agent and scope as `absent`, `current`, or `outdated`. Human mode shows descriptions and compact badges; machine mode adds exact paths and versions or digests.
- `install` refuses to replace an existing file without `--force`.
- `update` changes only recognized installed copies; `all` skips absent targets.
- `uninstall` removes only files the CLI owns and preserves unrelated content.
- An upgrade never installs absent copies. By default, installed copies change only through `skill update`. Optionally, the first run after an upgrade refreshes copies the CLI already installed, keyed on a version stamp written only after full success; the refresh is suppressible, never fails or alters the requested command's output, and its result is visible in `skill list` or `doctor`.

Test lifecycle commands in temporary global and project roots: absent, current, outdated, conflicting, forced replacement, update-all, conservative uninstall, and partial filesystem failure.

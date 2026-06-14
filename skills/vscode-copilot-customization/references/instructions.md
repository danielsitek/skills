# Custom Instructions

Always-on context and rules that apply automatically to all (or scoped) requests.

## File types

| Type                         | File / Location                          | Scope                           |
| ---------------------------- | ---------------------------------------- | ------------------------------- |
| Workspace-wide (Copilot)     | `.github/copilot-instructions.md`        | All requests in workspace       |
| Workspace-wide (multi-agent) | `AGENTS.md` anywhere in workspace        | All agents (Claude, Copilot, …) |
| File-scoped                  | `.github/instructions/*.instructions.md` | Files matching `applyTo` glob   |
| User-level                   | VS Code user profile                     | All workspaces                  |

## Frontmatter (`.instructions.md`)

```yaml
---
name: "React Standards"          # Optional – shown in UI
description: "React/TSX rules"   # Optional – describes scope
applyTo: "**/*.tsx"              # Glob – omit or use "**" for all files
---
```

> For `.claude/rules/*.md` files (Claude Code format), use `paths: ["**/*.ts"]` instead of `applyTo`.

## Template: project-wide

```markdown
---
applyTo: "**"
---
# Project Coding Standards

## General
- Use TypeScript for all new code; strict mode enabled.
- Prefer functional patterns; avoid classes unless needed.
- Max line length: 100 chars. 2-space indentation.

## Naming
- PascalCase: components, interfaces, types, enums.
- camelCase: variables, functions, hooks.
- ALL_CAPS: constants.

## Error handling
- Use try/catch for all async operations.
- Always log errors with context (module + function name).

## Testing
- Jest + React Testing Library.
- One test file per module, co-located (`*.test.ts`).
```

## Template: scoped (TypeScript only)

```markdown
---
name: "TypeScript Standards"
applyTo: "**/*.ts,**/*.tsx"
---
# TypeScript Rules

- Enable `strictNullChecks` and `noImplicitAny`.
- Prefer `interface` over `type` for object shapes.
- Use `unknown` instead of `any` for external data.
- Always type function return values explicitly.
```

## Key settings

```json
"github.copilot.chat.codeGeneration.useInstructionFiles": true,
"chat.instructionsFilesLocations": {
  ".github/instructions": true
},
"chat.useAgentsMdFile": true
```

## AI-assisted creation

```
/init                  → generate workspace-wide copilot-instructions.md
/create-instruction    → generate a targeted .instructions.md file
```

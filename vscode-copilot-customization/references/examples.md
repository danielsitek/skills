# Real-World Examples by Use Case

## Use Case: Next.js / React Project Setup

### `.github/copilot-instructions.md`

```markdown
---
applyTo: "**"
---
# Project: Next.js E-commerce App

## Stack
- Next.js 15 (App Router), React 19, TypeScript 5
- Tailwind CSS v4, shadcn/ui
- Zustand for client state, TanStack Query for server state
- Prisma + PostgreSQL

## Conventions
- Server Components by default. Add `"use client"` only when needed.
- Co-locate components: `src/components/FeatureName/FeatureName.tsx + index.ts`
- Use `@/` alias for `src/` imports.
- No barrel re-exports from `app/` directory.

## Code style
- TypeScript strict mode. No `any`.
- Prefer `const` over `let`. No `var`.
- Named exports everywhere. Default export only for Next.js pages.
- Zod for all external data validation.
```

### `.github/instructions/tailwind.instructions.md`

```markdown
---
name: "Tailwind CSS Rules"
applyTo: "**/*.tsx,**/*.jsx"
---
# Tailwind CSS Conventions

- Use `cn()` utility from `@/lib/utils` for conditional class merging.
- Use design tokens (custom CSS vars) over arbitrary values.
- Responsive: mobile-first. Use `sm:`, `md:`, `lg:` breakpoints.
- Dark mode: use `dark:` variants. Never hardcode colors.
- Extract repeated class groups into components, not `@apply`.
```

---

## Use Case: Code Review Agent

### `.github/agents/reviewer.agent.md`

```markdown
---
name: "Reviewer"
description: "Thorough code review: quality, security, performance, accessibility. No code edits."
tools:
  - "read"
  - "search"
  - "fetch"
  - "vscode/askQuestions"
model: "claude-opus-4-6 (copilot)"
---
# Code Reviewer

You are a senior engineer. **Analyze only — never write or edit code.**

## Review focus
1. **Security**: XSS, SQL injection, insecure direct object references, missing auth checks
2. **Performance**: N+1 queries, unnecessary re-renders, missing memoization
3. **Correctness**: edge cases, null handling, async errors
4. **Standards**: adherence to [project rules](../copilot-instructions.md)
5. **Accessibility**: ARIA roles, keyboard nav, color contrast

## Output format
Use these severity markers:
- 🔴 **Critical** (blocking) – security holes, data loss risk
- 🟡 **Warning** (should fix) – performance, correctness
- 🟢 **Suggestion** (optional) – style, readability

For each finding: file path, line(s), explanation, suggested fix.
```

---

## Use Case: Component Generator Prompt

### `.github/prompts/new-component.prompt.md`

```markdown
---
name: "new-component"
description: "Scaffold a typed React component with Tailwind, stories, and tests"
agent: "agent"
tools:
  - "edit"
  - "search/codebase"
  - "vscode/askQuestions"
---
# New React Component

Ask the user for:
1. **Component name** (PascalCase)
2. **Props** (list with types)
3. **Is it a server component?** (yes/no)

Then create these files under `src/components/<Name>/`:

**`<Name>.tsx`**
- TypeScript interface for props (named `<Name>Props`)
- Functional component with Tailwind classes
- Accessible markup (roles, aria-labels where needed)
- Add `"use client"` only if interactive

**`<Name>.test.tsx`**
- Jest + React Testing Library
- At minimum: renders without crashing, renders with props

**`index.ts`**
- Barrel export: `export { default } from './<Name>'`
- `export type { <Name>Props } from './<Name>'`

Follow [project standards](../copilot-instructions.md).
```

---

## Use Case: Auto-formatter + Linter Hooks

Two separate files — different responsibilities, consistent naming.

### `.github/hooks/post-tool.json`

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "type": "command",
        "command": "test -f \"$TOOL_INPUT_FILE_PATH\" && bunx biome check --write \"$TOOL_INPUT_FILE_PATH\" 2>/dev/null || true",
        "windows": "if exist \"%TOOL_INPUT_FILE_PATH%\" bunx biome check --write \"%TOOL_INPUT_FILE_PATH%\" 2>nul",
        "timeout": 30
      }
    ]
  }
}
```

### `.github/hooks/session-end.json`

```json
{
  "hooks": {
    "Stop": [
      {
        "type": "command",
        "command": "bun run typecheck 2>&1 | tail -30",
        "timeout": 60
      }
    ]
  }
}
```

---

## Use Case: Database Migration Skill

### `.github/skills/db-migration/SKILL.md`

```markdown
---
name: "db-migration"
description: >
  Guide for creating Prisma database migrations. Use when asked to add models,
  change schema, create migrations, or update the database structure.
hint: "[migration description]"
---
# Database Migrations (Prisma)

## When to use
- Adding or modifying Prisma schema models
- Creating new migrations
- Resolving migration conflicts

## Workflow

1. Modify `prisma/schema.prisma`
2. Run: `npx prisma migrate dev --name <description>`
3. Run: `npx prisma generate` to update the client
4. Update seed file if needed: `prisma/seed.ts`

## Naming conventions
- Migration names: `snake_case`, descriptive (`add_user_roles`, `rename_product_sku`)
- Model names: PascalCase singular (`User`, `Product`)
- Field names: camelCase (`createdAt`, `userId`)

## Common patterns

See [schema-patterns.md](./references/schema-patterns.md) for:
- Soft delete pattern
- Many-to-many with extra fields
- Polymorphic relations
```

---

## Use Case: Plan → Implement Workflow (Multi-agent)

### `.github/agents/planner.agent.md`

```markdown
---
name: "Planner"
description: "Creates detailed implementation plans. Does not write code."
tools:
  - "read"
  - "search"
  - "fetch"
  - "githubRepo"
model: "claude-opus-4-6 (copilot)"
handoffs:
  - label: "Implement Plan"
    agent: "agent"
    prompt: "Implement the plan above step by step. Check off each item as you complete it."
    send: false
---
# Planner Agent

Generate a **detailed implementation plan only**. No code edits.

## Output structure

```markdown
## Overview
[What this feature does and why]

## Files
| File | Action | Reason |
| ---- | ------ | ------ |

## Steps
1. [Step 1 – brief description]
   - Detail
   - Detail

## Dependencies / risks
- [Things to watch out for]

## Open questions
- [Decisions the developer needs to make]
```
```

---

## Use Case: TypeScript + ESLint Instructions (Monorepo)

### `.github/instructions/typescript.instructions.md`

```markdown
---
name: "TypeScript"
applyTo: "**/*.ts,**/*.tsx"
---
- Strict mode: no `any`, no `!` non-null assertions without a comment.
- Prefer `unknown` over `any` for external/API data.
- Generic functions: use descriptive type parameter names (`TItem` not `T`).
- Return types: always explicit on exported functions.
- Async functions: always handle errors; never swallow rejections.
- Use `satisfies` operator for object literals when type inference is needed.
```

### `.github/instructions/tests.instructions.md`

```markdown
---
name: "Testing"
applyTo: "**/*.test.ts,**/*.test.tsx,**/*.spec.ts"
---
- Pattern: Arrange-Act-Assert. One assertion per test when possible.
- Mock only at boundaries (API, DB, FS). Avoid mocking internal modules.
- Use `describe` blocks: outer = module name, inner = function/component name.
- Use `it('should ...')` naming, not `test('...')`.
- No `toBeTruthy()` / `toBeFalsy()` – use specific matchers.
- Clean up: always restore mocks with `afterEach(() => vi.restoreAllMocks())`.
```

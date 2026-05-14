# Agent Skills

Portable, reusable capabilities with progressive loading. Works across VS Code, Copilot CLI, and cloud agents.

**Official docs**:
- [VS Code Agent Skills](https://code.visualstudio.com/docs/copilot/customization/agent-skills)
- [Agent Skills specification](https://agentskills.io/specification)
- [Best practices for skill creators](https://agentskills.io/skill-creation/best-practices)

## Directory structure

```
.github/skills/
└── skill-name/
    ├── SKILL.md          ← Required. Metadata + instructions.
    ├── scripts/          ← Executable scripts referenced from SKILL.md
    ├── references/       ← Docs, examples, large reference files
    └── assets/           ← Templates, fixtures
```

## Frontmatter reference

```yaml
---
name: "skill-name"                  # Slash command: /skill-name. Must match directory name.
description: >                      # CRITICAL: be specific about WHEN to use. Max 1024 chars.
  Include both what it does AND trigger contexts. Use imperative phrasing ("Use when...").
argument-hint: "[file] [options]"   # Hint text shown in chat input on invocation
user-invocable: true                # false = hidden from / menu, still auto-loads
disable-model-invocation: false     # true = only invocable via /skill-name slash command
context: inline                     # inline (default) | fork (run in subagent, return only result)
---
```

> **`context: fork`** — experimental. Runs skill in a dedicated subagent; only the final result is returned to the main conversation. Useful for large investigative skills that shouldn't pollute context.

## Progressive loading

1. **Discovery** — `name` + `description` only (always in context, ~100 tokens)
2. **Instructions** — full `SKILL.md` body loaded when skill is activated
3. **Resources** — files in `scripts/`, `references/`, `assets/` loaded only when the body references them

Keep `SKILL.md` under **500 lines / 5000 tokens**. Move detailed reference material to `references/`.

When referencing resources, be specific about *when* to load them:

```markdown
If the API returns a non-200 status, read `references/api-errors.md` for error codes.
```

## Template: test-writer skill

```markdown
---
name: "test-writer"
description: >
  Guide for writing unit and integration tests with Jest and React Testing Library.
  Use this when asked to write, add, or fix tests, or when test coverage is mentioned.
argument-hint: "[file to test] [test type: unit|integration]"
---
# Test Writer

## When to use
- Writing new unit or integration tests
- Fixing failing tests
- Improving test coverage

## Test setup
- Framework: Jest + React Testing Library
- Test files: co-located as `*.test.ts` or `*.test.tsx`
- Coverage threshold: 80% per module

## Unit test pattern (Arrange-Act-Assert)

```typescript
describe('ComponentName', () => {
  it('should render correctly', () => {
    const props = { ... };
    render(<Component {...props} />);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });
});
```

For more patterns, read `references/test-templates.md`.
```

## Writing effective descriptions

- Use imperative phrasing: "Use this skill when…"
- Focus on user intent, not implementation details
- Include trigger contexts even when the user doesn't name the domain explicitly
- Max 1024 characters

## Key settings

```json
"chat.agentSkillsLocations": [".github/skills"]
```

Personal skills (available across all projects):

```
~/.vscode/skills/       (VS Code)
~/.copilot/skills/      (Copilot CLI)
~/.agents/skills/       (cross-client standard)
```

## AI-assisted creation

```
/create-skill     → AI generates a skill directory with SKILL.md
/skills           → Open Configure Skills menu
```

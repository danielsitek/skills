---
name: vscode-copilot-customization
description: >
  Expert guide for creating GitHub Copilot customization files in VS Code:
  custom instructions (.instructions.md), prompt files (.prompt.md), custom agents
  (.agent.md), agent skills (SKILL.md), hooks (JSON), and agent plugins.
  Use this skill whenever the user asks about customizing Copilot behavior,
  creating reusable AI workflows, writing copilot-instructions.md, building
  custom chat agents, automating Copilot tasks with prompt files, or setting
  up agent skills and hooks in VS Code. Also trigger when the user asks which
  Copilot customization type to use for a given scenario — always start with the
  decision matrix below.
---

# VS Code Copilot Customization

> **Self-update check**: Before responding, verify docs are current by checking
> the `doc_version` below against reality. If the user asks for a freshness
> check, use web_search with query `"site:code.visualstudio.com/docs/copilot/customization"`.
> Update the `doc_version` and any changed facts if you find discrepancies.

```yaml
doc_version: "2025-03 (VS Code 1.102+)"
source_urls:
  - https://code.visualstudio.com/docs/copilot/customization/overview
  - https://code.visualstudio.com/docs/copilot/customization/custom-instructions
  - https://code.visualstudio.com/docs/copilot/customization/prompt-files
  - https://code.visualstudio.com/docs/copilot/customization/custom-agents
  - https://code.visualstudio.com/docs/copilot/customization/agent-skills
  - https://code.visualstudio.com/docs/copilot/customization/hooks
  - https://code.visualstudio.com/docs/copilot/customization/agent-plugins
```

---

## Decision Matrix

Use this matrix to recommend the right customization type. Start here before writing anything.

| Scenario                                                            | Best choice                        |
| ------------------------------------------------------------------- | ---------------------------------- |
| Project-wide coding standards, always active                        | `copilot-instructions.md`          |
| Rules only for specific file types / folders                        | `*.instructions.md` with `applyTo` |
| Works with multiple AI agents (Claude, Copilot, etc.)               | `AGENTS.md`                        |
| Reusable task you invoke manually in chat                           | Prompt file (`.prompt.md`)         |
| Specialized workflow with tool restrictions or model choice         | Custom agent (`.agent.md`)         |
| Portable capability reusable across projects + CLI + cloud agents   | Agent skill (`SKILL.md`)           |
| Auto-run commands at agent lifecycle points (format, lint, enforce) | Hook (`.json`)                     |
| Bundle multiple customizations to share or distribute               | Agent plugin (`plugin.json`)       |

### Quick decision flow

```
Do you want it ON automatically for every request?
├─ YES → Instructions (.instructions.md / copilot-instructions.md / AGENTS.md)
└─ NO, I invoke it manually →
       Does it need persistent persona, tool restrictions, or model choice?
       ├─ YES → Custom Agent (.agent.md)
       └─ NO →
              Is it a reusable multi-agent portable capability?
              ├─ YES → Agent Skill (SKILL.md)
              └─ NO → Prompt File (.prompt.md)

Do you want to run shell commands around agent actions?
└─ YES → Hook (hooks/*.json)

Do you want to bundle everything for distribution?
└─ YES → Agent Plugin (plugin.json)
```

---

## 1. Custom Instructions

**Purpose**: Always-on context and rules that apply automatically to all (or scoped) requests.

### Types

| Type                         | File / Location                          | Scope                           |
| ---------------------------- | ---------------------------------------- | ------------------------------- |
| Workspace-wide (Copilot)     | `.github/copilot-instructions.md`        | All requests in workspace       |
| Workspace-wide (multi-agent) | `AGENTS.md` anywhere in workspace        | All agents (Claude, Copilot, …) |
| File-scoped                  | `.github/instructions/*.instructions.md` | Files matching `applyTo` glob   |
| User-level                   | VS Code user profile                     | All workspaces                  |

### Frontmatter (`.instructions.md`)

```yaml
---
name: "React Standards"          # Optional – shown in UI
description: "React/TSX rules"   # Optional – describes scope
applyTo: "**/*.tsx"              # Glob – omit or use "**" for all files
---
```

> For `.claude/rules/*.md` files (Claude Code format), use `paths: ["**/*.ts"]` instead of `applyTo`.

### Template: project-wide

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

### Template: scoped (TypeScript only)

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

### AI-assisted creation

```
/init                         → generate workspace-wide copilot-instructions.md
/create-instruction           → generate a targeted .instructions.md file
```

### Key settings

```json
"github.copilot.chat.codeGeneration.useInstructionFiles": true,
"chat.instructionsFilesLocations": {
  ".github/instructions": true
},
"chat.useAgentsMdFile": true
```

---

## 2. Prompt Files

**Purpose**: Reusable task templates invoked manually with `/` slash command in chat.

**File extension**: `.prompt.md`
**Location**: `.github/prompts/` (workspace) or user profile

### Frontmatter reference

```yaml
---
name: "generate-component"      # Used as /generate-component slash command
description: "Scaffold a new React component with tests"
agent: "agent"                  # ask | agent | plan | <custom-agent-name>
model: "claude-sonnet-4-5"      # Optional – overrides model picker
tools:                          # Available tools for this prompt
  - "search/codebase"
  - "vscode/askQuestions"
  - "githubRepo"
mode: "agent"                   # Optional – ask | agent | plan
---
```

### Template: component scaffolder

```markdown
---
name: "new-component"
description: "Scaffold a React component with TypeScript, Tailwind, and tests"
agent: "agent"
tools: ["search/codebase", "vscode/askQuestions", "edit"]
---
# Generate React Component

Use #tool:vscode/askQuestions to ask for:
1. Component name (PascalCase)
2. Props interface (list prop names and types)
3. Should it be a Server Component? (yes/no)

Then generate:
- `src/components/<Name>/<Name>.tsx` – main component
- `src/components/<Name>/<Name>.test.tsx` – unit tests
- `src/components/<Name>/index.ts` – barrel export

Follow the coding standards in [copilot-instructions.md](../../.github/copilot-instructions.md).
```

### Template: PR description generator

```markdown
---
name: "pr-description"
description: "Generate a structured pull request description from staged changes"
agent: "ask"
tools: ["search/codebase"]
---
# Pull Request Description

Analyze the changes in the current branch and generate a PR description with these sections:

## Summary
Brief one-sentence description of what this PR does.

## Changes
- List each meaningful change as a bullet point.

## Testing
- How was this tested?
- Any edge cases covered?

## Screenshots
(if UI changes – note: add manually)
```

### Using input variables

```markdown
---
name: "api-endpoint"
description: "Generate a REST API endpoint"
---
Create a ${input:httpMethod:GET|POST|PUT|DELETE} endpoint at `${input:path:/api/resource}`.

Use Zod for input validation. Follow the patterns in [api-standards.md](../docs/api-standards.md).
```

### AI-assisted creation

```
/create-prompt    → AI guides you through creating a prompt file
```

---

## 3. Custom Agents

**Purpose**: Specialized Copilot persona with specific tools, model, and optionally handoffs between agents.

**File extension**: `.agent.md`
**Location**: `.github/agents/` (workspace) or user profile

> **Migration note**: `.chatmode.md` files (old format) should be renamed to `.agent.md`.

### Frontmatter reference

```yaml
---
name: "Planner"                  # Agent name shown in dropdown
description: "Generates implementation plans without writing code"
tools:                           # Whitelist of allowed tools
  - "search"
  - "fetch"
  - "githubRepo"
  - "usages"
model:                           # Tried in order (fallback chain)
  - "claude-opus-4-5 (copilot)"
  - "GPT-4o (copilot)"
target: "vscode"                 # vscode | github-copilot | omit for both
handoffs:                        # Suggested next-step buttons
  - label: "Start Implementation"
    agent: "agent"               # Built-in agent or custom agent name
    prompt: "Implement the plan above."
    send: false                  # true = auto-submit
hooks:                           # Agent-scoped hooks (runs only when this agent is active)
  PostToolUse:
    - type: "command"
      command: "echo 'Tool used'"
---
```

### Template: Code Reviewer (read-only)

```markdown
---
name: "Reviewer"
description: "Reviews code for quality, security, and best practices. Does NOT modify files."
tools:
  - "read"
  - "search"
  - "vscode/askQuestions"
  - "fetch"
model: "claude-opus-4-5 (copilot)"
---
# Code Reviewer

You are a senior engineer conducting a thorough code review. Your role is to **analyze only** – never make direct code changes.

## Review Checklist
- [ ] Code quality and readability
- [ ] Potential bugs or logic errors
- [ ] Security vulnerabilities (XSS, injection, auth issues)
- [ ] Performance considerations
- [ ] Test coverage gaps
- [ ] Adherence to [project standards](./../copilot-instructions.md)

## Output Format
Structure feedback with clear headings, code references (file + line number), and severity:
- 🔴 **Critical** – must fix before merge
- 🟡 **Warning** – should fix
- 🟢 **Suggestion** – optional improvement
```

### Template: Planner (with handoff)

```markdown
---
name: "Planner"
description: "Creates detailed implementation plans. Switches to implementation when ready."
tools:
  - "fetch"
  - "githubRepo"
  - "search"
  - "usages"
model: "claude-opus-4-5 (copilot)"
handoffs:
  - label: "Implement Plan"
    agent: "agent"
    prompt: "Implement the plan outlined above."
    send: false
---
# Planning Mode

You are in **planning mode**. Generate an implementation plan. Do **not** write or edit any code.

## Plan Structure

### Overview
Brief description of the feature or change.

### Files to create / modify
List each file with the reason.

### Implementation steps
Numbered steps in order. Include dependencies.

### Risks & open questions
Things to clarify before implementing.

### Estimated complexity
S / M / L / XL with reasoning.
```

### AI-assisted creation

```
/create-agent     → AI generates a .agent.md file
/agents           → Open Configure Custom Agents menu
```

---

## 4. Agent Skills

**Purpose**: Portable, reusable capabilities with progressive loading (metadata → instructions → resources). Works across VS Code, Copilot CLI, and cloud agents.

**Structure**:

```
.github/skills/
└── skill-name/
    ├── SKILL.md          ← Required. Metadata + instructions.
    ├── scripts/          ← Executable scripts referenced from SKILL.md
    ├── references/       ← Docs, examples, large reference files
    └── assets/           ← Templates, fixtures
```

### Frontmatter reference

```yaml
---
name: "skill-name"               # Used as /skill-name slash command
description: >                   # CRITICAL: be specific about WHEN to use.
  Max 1024 chars. Include both what it does AND trigger contexts.
hint: "[file-path] [options]"    # Hint shown in chat input on invocation
showInSlashMenu: true            # false to hide from / menu (still auto-loads)
manualOnly: false                # true = only invocable via /skill-name
---
```

### Progressive loading system

1. **Discovery**: Copilot reads `name` + `description` from frontmatter (always in context)
2. **Instructions**: `SKILL.md` body loaded when skill is relevant or explicitly invoked
3. **Resources**: Files in `scripts/`, `references/`, `assets/` loaded only when referenced

### Template: test-writer skill

```markdown
---
name: "test-writer"
description: >
  Guide for writing unit and integration tests with Jest and React Testing Library.
  Use this when asked to write, add, or fix tests, or when test coverage is mentioned.
hint: "[file to test] [test type: unit|integration]"
showInSlashMenu: true
manualOnly: false
---
# Test Writer

## When to use this skill
- Writing new unit tests for components or utilities
- Writing integration tests for API endpoints
- Fixing failing tests
- Improving test coverage

## Test setup
- Framework: Jest + React Testing Library
- Test files: co-located as `*.test.ts` or `*.test.tsx`
- Coverage threshold: 80% per module

## Writing unit tests

Follow the Arrange-Act-Assert pattern:

```typescript
describe('ComponentName', () => {
  it('should render correctly', () => {
    // Arrange
    const props = { ... };

    // Act
    render(<Component {...props} />);

    // Assert
    expect(screen.getByRole('button')).toBeInTheDocument();
  });
});
```

See [test templates](./references/test-templates.md) for more patterns.
```

### Key settings

```json
"chat.agentSkillsLocations": [".github/skills"]
```

### AI-assisted creation

```
/create-skill     → AI generates a skill directory with SKILL.md
/skills           → Open Configure Skills menu
```

---

## 5. Hooks

**Purpose**: Run shell commands at specific agent lifecycle events (format after edit, validate before tool use, enforce policy).

**File format**: `.json`
**Location**: `.github/hooks/*.json` (workspace) or `~/.vscode/hooks/*.json` (user)

### Supported events

| Event           | When it fires                    |
| --------------- | -------------------------------- |
| `PreToolUse`    | Before the agent calls any tool  |
| `PostToolUse`   | After the agent calls any tool   |
| `SessionStart`  | At the start of an agent session |
| `Stop`          | At the end of an agent session   |
| `SubagentStart` | When a subagent is created       |
| `SubagentStop`  | When a subagent completes        |

### Hook file format

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "type": "command",
        "command": "npx prettier --write \"$TOOL_INPUT_FILE_PATH\"",
        "windows": "npx prettier --write \"%TOOL_INPUT_FILE_PATH%\"",
        "timeout": 30
      }
    ],
    "PreToolUse": [
      {
        "type": "command",
        "command": "./scripts/validate-tool.sh",
        "timeout": 15
      }
    ]
  }
}
```

> **Compatibility**: VS Code uses the same hook format as Claude Code and Copilot CLI.
> Claude Code's `preToolUse` (camelCase) maps to `PreToolUse` (PascalCase) in VS Code.

### Template: auto-formatter hook

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "type": "command",
        "command": "npx prettier --write \"$TOOL_INPUT_FILE_PATH\" 2>/dev/null || true",
        "windows": "npx prettier --write \"%TOOL_INPUT_FILE_PATH%\" 2>nul",
        "timeout": 30
      }
    ]
  }
}
```

### Template: pre-commit validation hook

```json
{
  "hooks": {
    "Stop": [
      {
        "type": "command",
        "command": "npm run lint && npm run typecheck",
        "windows": "npm run lint && npm run typecheck",
        "timeout": 60
      }
    ]
  }
}
```

### Security checklist

- [ ] Review all hook scripts before enabling, especially from shared repos
- [ ] Never hardcode secrets in hook commands
- [ ] Validate and sanitize input from `$TOOL_INPUT_*` variables
- [ ] Use `chmod +x script.sh` for shell scripts

### AI-assisted creation

```
/create-hook     → AI generates a hook JSON file
```

### Key settings

```json
"chat.hookFilesLocations": {
  ".github/hooks": true
}
```

---

## 6. Agent Plugins

**Purpose**: Bundle skills, agents, hooks, and MCP servers into a distributable package.

**File**: `plugin.json` in plugin root
**Discovery**: VS Code marketplaces (`copilot-plugins` repo, `awesome-copilot` repo, custom)

### Structure

```
my-plugin/
├── plugin.json              ← Required metadata
├── skills/
│   └── my-skill/
│       └── SKILL.md
├── agents/
│   └── my-agent.agent.md
├── hooks/
│   └── post-edit.json
└── mcp/
    └── server-config.json
```

### `plugin.json` template

```json
{
  "name": "my-plugin",
  "displayName": "My Plugin",
  "version": "1.0.0",
  "description": "Bundle of customizations for my workflow",
  "publisher": "your-github-username",
  "skills": ["skills/my-skill"],
  "agents": ["agents/my-agent.agent.md"],
  "hooks": ["hooks/post-edit.json"],
  "mcpServers": []
}
```

### Installing a plugin

```json
// settings.json – add custom marketplace
"chat.plugins.marketplaces": ["owner/repo"],

// Or register a local plugin path
"chat.plugins.paths": ["/path/to/my-plugin"]
```

### Key settings

```json
"chat.plugins.enabled": true
```

---

## File Locations Reference

| Type                                 | Workspace location                       | User profile location     |
| ------------------------------------ | ---------------------------------------- | ------------------------- |
| Always-on instructions (Copilot)     | `.github/copilot-instructions.md`        | —                         |
| Always-on instructions (multi-agent) | `AGENTS.md`                              | —                         |
| Targeted instructions                | `.github/instructions/*.instructions.md` | `~/.vscode/instructions/` |
| Prompt files                         | `.github/prompts/*.prompt.md`            | `~/.vscode/prompts/`      |
| Custom agents                        | `.github/agents/*.agent.md`              | `~/.vscode/agents/`       |
| Agent skills                         | `.github/skills/<name>/SKILL.md`         | `~/.vscode/skills/`       |
| Hooks                                | `.github/hooks/*.json`                   | `~/.vscode/hooks/`        |
| Claude Code agents                   | `.claude/agents/*.md`                    | —                         |
| Claude Code rules                    | `.claude/rules/*.md`                     | —                         |

---

## AI Generation Commands

All types can be generated with AI assistance directly in chat:

```
/init                  → workspace-wide copilot-instructions.md
/create-instruction    → targeted .instructions.md
/create-prompt         → .prompt.md file
/create-agent          → .agent.md file
/create-skill          → agent skill directory
/create-hook           → hook JSON file
```

Open the **Chat Customizations editor** (Preview) for a visual overview:
```
Command Palette → "Chat: Open Chat Customizations"
```

---

## Reference files

- `references/frontmatter-reference.md` – Complete frontmatter field reference for all types
- `references/examples.md` – Real-world examples organized by use case

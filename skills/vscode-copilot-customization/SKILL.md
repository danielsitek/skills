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

## Decision Matrix

Use this matrix to recommend the right customization type. Always start here.

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

Always-on context and rules. Stored in `.github/copilot-instructions.md` (workspace-wide), `AGENTS.md` (multi-agent), or `*.instructions.md` (file-scoped via `applyTo` glob).

Read `references/instructions.md` when asked to create, write, or configure custom instructions.

---

## 2. Prompt Files

Reusable task templates invoked manually via `/` slash command. Stored in `.github/prompts/*.prompt.md`.

Read `references/prompt-files.md` when asked to create a prompt file or reusable chat task.

---

## 3. Custom Agents

Specialized Copilot persona with tool whitelist, model choice, and optional handoffs. Stored in `.github/agents/*.agent.md`.

Read `references/custom-agents.md` when asked to create a custom agent or chat mode.

---

## 4. Agent Skills

Portable, progressive-loading capabilities that work across VS Code, Copilot CLI, and cloud agents. Stored in `.github/skills/<name>/SKILL.md`.

Read `references/agent-skills.md` when asked to create a skill or when the user asks about SKILL.md format, frontmatter fields, or skill best practices.

---

## 5. Hooks

Shell commands triggered at agent lifecycle events (`PostToolUse`, `Stop`, etc.). Stored in `.github/hooks/*.json`.

Read `references/hooks.md` when asked to create a hook, set up auto-formatting, or run commands around agent actions.

---

## 6. Agent Plugins

Bundle skills, agents, hooks, and MCP servers for distribution. Defined in `plugin.json`.

Read `references/plugins.md` when asked to create, publish, or install an agent plugin.

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

```
/init                  → workspace-wide copilot-instructions.md
/create-instruction    → targeted .instructions.md
/create-prompt         → .prompt.md file
/create-agent          → .agent.md file
/create-skill          → agent skill directory
/create-hook           → hook JSON file
```

Open the **Chat Customizations editor** for a visual overview:
```
Command Palette → "Chat: Open Chat Customizations"
```

---

## Reference files

- `references/instructions.md` – Custom instructions templates and settings
- `references/prompt-files.md` – Prompt file templates and input variables
- `references/custom-agents.md` – Agent templates and handoff configuration
- `references/agent-skills.md` – Skill format, progressive loading, official docs
- `references/hooks.md` – Hook templates, events, naming convention
- `references/plugins.md` – Plugin structure and distribution
- `references/frontmatter-reference.md` – Complete frontmatter field reference for all types
- `references/examples.md` – Real-world examples organized by use case

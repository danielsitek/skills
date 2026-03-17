# Frontmatter Field Reference

Complete list of supported YAML frontmatter fields for each customization type.

---

## Instructions (`.instructions.md`)

| Field         | Type        | Required | Description                                                                         |
| ------------- | ----------- | -------- | ----------------------------------------------------------------------------------- |
| `name`        | string      | No       | Display name in the UI                                                              |
| `description` | string      | No       | Describes what these instructions do                                                |
| `applyTo`     | glob string | No       | Files to apply to. Omit or `"**"` for all files. Examples: `"**/*.tsx"`, `"src/**"` |

> **Note**: For `.claude/rules/*.md` (Claude Rules format), use `paths` (array of globs) instead of `applyTo`.

---

## Prompt Files (`.prompt.md`)

| Field         | Type     | Required | Description                                                                                                                 |
| ------------- | -------- | -------- | --------------------------------------------------------------------------------------------------------------------------- |
| `name`        | string   | No       | Used as `/name` slash command. Defaults to filename.                                                                        |
| `description` | string   | No       | Shown in the / command list                                                                                                 |
| `agent`       | string   | No       | `ask` \| `agent` \| `plan` \| `<custom-agent-name>`. Defaults to current agent; defaults to `agent` if tools are specified. |
| `model`       | string   | No       | Model to use. Format: `"claude-sonnet-4-5 (copilot)"` or `"GPT-4o (copilot)"`                                               |
| `tools`       | string[] | No       | Available tools. Unsupported tools are ignored. Use `"<server-name>/*"` for all MCP tools.                                  |
| `mode`        | string   | No       | `ask` \| `agent` \| `plan`                                                                                                  |
| `hint`        | string   | No       | Hint text shown in chat input when prompt is invoked                                                                        |

### Tool name examples

```yaml
tools:
  - "search"                    # Workspace code search
  - "search/codebase"           # Codebase-specific search
  - "fetch"                     # Fetch URLs
  - "edit"                      # File editing
  - "read"                      # File reading (no edits)
  - "githubRepo"                # Search GitHub repos
  - "vscode/askQuestions"       # Prompt user for input
  - "usages"                    # Find symbol usages
  - "browser"                   # Browser tool
  - "agent"                     # Spawn subagents
  - "my-mcp-server/*"           # All tools from MCP server
```

---

## Custom Agents (`.agent.md`)

| Field         | Type               | Required | Description                                                              |
| ------------- | ------------------ | -------- | ------------------------------------------------------------------------ |
| `name`        | string             | Yes      | Agent name shown in dropdown                                             |
| `description` | string             | Yes      | Describes the agent's purpose and when to use it                         |
| `tools`       | string[]           | No       | Whitelist of tools. Omit to allow all tools. Same names as prompt files. |
| `model`       | string \| string[] | No       | Model or fallback list. Format: `"Model Name (vendor)"`                  |
| `target`      | string             | No       | `vscode` \| `github-copilot`. Omit for both.                             |
| `handoffs`    | object[]           | No       | Suggested next-step buttons (see below)                                  |
| `hooks`       | object             | No       | Agent-scoped hooks (same format as hook JSON files)                      |

### Handoff object fields

| Field    | Type    | Required | Description                            |
| -------- | ------- | -------- | -------------------------------------- |
| `label`  | string  | Yes      | Button text                            |
| `agent`  | string  | Yes      | Target agent identifier                |
| `prompt` | string  | No       | Pre-filled prompt for the target agent |
| `send`   | boolean | No       | `true` = auto-submit. Default: `false` |
| `model`  | string  | No       | Model to use when handoff executes     |

---

## Agent Skills (`SKILL.md`)

| Field             | Type    | Required | Description                                                                                               |
| ----------------- | ------- | -------- | --------------------------------------------------------------------------------------------------------- |
| `name`            | string  | Yes      | Skill identifier, used as `/name` slash command                                                           |
| `description`     | string  | Yes      | What it does AND when to use it. Max 1024 chars. Be specific about trigger contexts.                      |
| `hint`            | string  | No       | Hint text shown in chat input on invocation                                                               |
| `showInSlashMenu` | boolean | No       | Show in `/` menu. Default: `true`                                                                         |
| `manualOnly`      | boolean | No       | If `true`, only invocable via `/name`. Default: `false`. Set to `true` if auto-loading is too aggressive. |

---

## Hooks (JSON)

```typescript
interface HookConfig {
  hooks: {
    [event: string]: HookCommand[];
  }
}

interface HookCommand {
  type: "command";          // Required: always "command"
  command: string;          // Default / Linux / macOS command
  windows?: string;         // Windows-specific command
  linux?: string;           // Linux-specific command
  osx?: string;             // macOS-specific command
  timeout?: number;         // Seconds. Default: 30
}
```

### Environment variables available in hook commands

| Variable                | Available in                | Description                   |
| ----------------------- | --------------------------- | ----------------------------- |
| `$TOOL_INPUT_FILE_PATH` | `PreToolUse`, `PostToolUse` | Path of the file being edited |
| `$TOOL_NAME`            | All tool events             | Name of the tool being called |
| `$SESSION_ID`           | All events                  | Current agent session ID      |

### Supported hook events

| Event           | Fires when                  |
| --------------- | --------------------------- |
| `PreToolUse`    | Before agent calls any tool |
| `PostToolUse`   | After agent calls any tool  |
| `SessionStart`  | Agent session starts        |
| `Stop`          | Agent session ends          |
| `SubagentStart` | Subagent is created         |
| `SubagentStop`  | Subagent completes          |

---

## Model Name Format

When specifying models in frontmatter, use the qualified format:

```yaml
# Single model
model: "claude-opus-4-6 (copilot)"

# Fallback chain (agents only)
model:
  - "claude-opus-4-6 (copilot)"
  - "GPT-4o (copilot)"
```

Common model names (verify in VS Code's model picker for current list):
- `claude-sonnet-4-5 (copilot)`
- `claude-opus-4-5 (copilot)`
- `GPT-4o (copilot)`
- `GPT-4.1 (copilot)`
- `o3 (copilot)`

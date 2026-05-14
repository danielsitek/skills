# Hooks

Run shell commands at specific agent lifecycle events — format after edits, validate before tool use, enforce policy.

**File format**: `.json`
**Location**: `.github/hooks/*.json` (workspace) or `~/.vscode/hooks/*.json` (user)

## Supported events

| Event           | When it fires                    |
| --------------- | -------------------------------- |
| `PreToolUse`    | Before the agent calls any tool  |
| `PostToolUse`   | After the agent calls any tool   |
| `SessionStart`  | At the start of an agent session |
| `Stop`          | At the end of an agent session   |
| `SubagentStart` | When a subagent is created       |
| `SubagentStop`  | When a subagent completes        |
****
## File naming convention

One file = one logical responsibility. Never name files after the project or create a generic `copilot.json`.

| File               | Events inside                   | Purpose                                     |
| ------------------ | ------------------------------- | ------------------------------------------- |
| `post-tool.json`   | `PostToolUse`                   | Format / lint after every tool call         |
| `session-end.json` | `Stop`                          | Typecheck / validate at end of session      |
| `pre-tool.json`    | `PreToolUse`                    | Block dangerous operations before execution |
| `subagent.json`    | `SubagentStart`, `SubagentStop` | Subagent monitoring                         |

Rules:
- **Split by responsibility**, not by event count. `PostToolUse` (formatting) and `Stop` (typecheck) serve different purposes → separate files.
- **Group related events** in one file. `SubagentStart` + `SubagentStop` belong together → one file.
- **Never merge unrelated events** into one file to reduce count.
- **Always use these exact filenames.** Consistent names let users know what each file does without opening it.

## Hook file format

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
    ]
  }
}
```

> **Compatibility**: VS Code uses the same hook format as Claude Code and Copilot CLI.
> Claude Code's `preToolUse` (camelCase) maps to `PreToolUse` (PascalCase) in VS Code.

## Environment variables

| Variable                | Available in                | Description                   |
| ----------------------- | --------------------------- | ----------------------------- |
| `$TOOL_INPUT_FILE_PATH` | `PreToolUse`, `PostToolUse` | Path of the file being edited |
| `$TOOL_NAME`            | All tool events             | Name of the tool being called |
| `$SESSION_ID`           | All events                  | Current agent session ID      |

## Template: `post-tool.json` (formatter)

Detect the formatter from `package.json` devDependencies. Do not default to Prettier if the project uses Biome.

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "type": "command",
        "command": "test -f \"$TOOL_INPUT_FILE_PATH\" && npx prettier --write \"$TOOL_INPUT_FILE_PATH\" 2>/dev/null || true",
        "windows": "if exist \"%TOOL_INPUT_FILE_PATH%\" npx prettier --write \"%TOOL_INPUT_FILE_PATH%\" 2>nul",
        "timeout": 30
      }
    ]
  }
}
```

## Template: `session-end.json` (typecheck / lint)

Detect the package manager (`npm`, `bun`, `pnpm`, `yarn`) and available scripts (`typecheck`, `lint`, `check`) from `package.json`.

```json
{
  "hooks": {
    "Stop": [
      {
        "type": "command",
        "command": "npm run typecheck 2>&1 | tail -30",
        "timeout": 60
      }
    ]
  }
}
```

## Template: `pre-tool.json` (policy enforcement)

```json
{
  "hooks": {
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

## After creating a hook file

**Always run this automatically** after writing any hook JSON file. The script verifies (and if needed updates) `.vscode/settings.json` so the hook directory is registered:

```bash
node scripts/ensure-hook-setting.js
```

See [scripts/ensure-hook-setting.js](../scripts/ensure-hook-setting.js) for what it does.

> The path above is relative to this skill's directory — the agent resolves it automatically regardless of where the skill is installed.

The script:
- Does **nothing** if `chat.hookFilesLocations` already contains `".github/hooks": true`
- **Adds** the entry if the key is missing
- **Merges** the entry if the key exists but is missing `".github/hooks"`
- Creates `.vscode/settings.json` if the file doesn't exist yet

## Security checklist

- [ ] Review all hook scripts before enabling, especially from shared repos
- [ ] Never hardcode secrets in hook commands
- [ ] Validate and sanitize input from `$TOOL_INPUT_*` variables
- [ ] Use `chmod +x script.sh` for shell scripts

## Key settings

```json
"chat.hookFilesLocations": {
  ".github/hooks": true
}
```

## AI-assisted creation

```
/create-hook     → AI generates a hook JSON file
```

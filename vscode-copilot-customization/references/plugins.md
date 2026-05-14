# Agent Plugins

Bundle skills, agents, hooks, and MCP servers into a distributable package.

**File**: `plugin.json` in plugin root
**Discovery**: VS Code marketplaces (`copilot-plugins` repo, `awesome-copilot` repo, custom)

## Directory structure

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

## `plugin.json` template

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

## Installing a plugin

```json
// settings.json – add custom marketplace
"chat.plugins.marketplaces": ["owner/repo"],

// Or register a local plugin path
"chat.plugins.paths": ["/path/to/my-plugin"]
```

## Key settings

```json
"chat.plugins.enabled": true
```

## Notes

- When a skill is bundled in a plugin, its slash command is prefixed with the plugin name: `/my-plugin:skill-name`. Do **not** add namespace prefixes manually to the `name` field — this causes the skill to silently fail to load.
- Skills, agents, and hooks inside a plugin follow the same file format as standalone ones.

# Prompt Files

Reusable task templates invoked manually with the `/` slash command in chat.

**File extension**: `.prompt.md`
**Location**: `.github/prompts/` (workspace) or user profile

## Frontmatter reference

```yaml
---
name: "generate-component"      # Used as /generate-component slash command
description: "Scaffold a new React component with tests"
agent: "agent"                  # ask | agent | plan | <custom-agent-name>
argument-hint: "[component-name]" # Optional – hint shown in chat input on invocation
model: "claude-sonnet-4-5"      # Optional – overrides model picker
tools:                          # Available tools for this prompt
  - "search/codebase"
  - "vscode/askQuestions"
  - "githubRepo"
---
```

## Input variables

Use `${input:name:default}` or `${input:name:option1|option2}` to prompt for values at run time:

```markdown
Create a ${input:httpMethod:GET|POST|PUT|DELETE} endpoint at `${input:path:/api/resource}`.
```

## Template: component scaffolder

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

## Template: PR description generator

```markdown
---
name: "pr-description"
description: "Generate a structured pull request description from staged changes"
agent: "ask"
tools: ["search/codebase"]
---
# Pull Request Description

Analyze the changes in the current branch and generate a PR description with:

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

## AI-assisted creation

```
/create-prompt    → AI guides you through creating a prompt file
```

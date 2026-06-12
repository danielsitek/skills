# handoff-invoke

Load a previously saved handoff file from `.handoffs/`, orient on what it contains, and resume the parked task.

## Usage

Trigger with phrases like: *"invoke handoff 3"*, *"open handoff-0002"*, *"let's pick up that handoff"*, *"resume the handoff about X"*.

You can reference a handoff by number or by topic — the skill will find the best match.

## What it does

1. Loads the handoff file
2. Gives you a full briefing (title, why parked, context, task)
3. Checks the current project state against the snapshot to flag anything stale
4. Asks how you'd like to proceed

Invoking a handoff does **not** delete it. Use `handoff-close` when done.

## Workflow

```
handoff-create → handoff-list → handoff-invoke → handoff-close
```

## Troubleshooting

- **Handoff not found by number** — the skill lists available handoffs. Use `handoff-list` to see all.
- **Ambiguous topic match** — the skill shows candidates and asks which one to open.

## Installation

```bash
npx skills@latest add danielsitek/skills/handoff-invoke
```

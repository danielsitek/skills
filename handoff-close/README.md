# handoff-close

Close a resolved handoff by number and delete its file from `.handoffs/`.

## Usage

Trigger with phrases like: *"close handoff 2"*, *"handoff 3 is done"*, *"remove that handoff"*, *"delete handoff-0001"*.

You can reference by number or topic. The skill always shows what will be deleted and asks for confirmation before removing the file.

## Workflow

```
handoff-create → handoff-list → handoff-invoke → handoff-close
```

## Troubleshooting

- **No `.handoffs/` directory** — the skill will tell you there is nothing to close.
- **Handoff not found** — the skill lists what exists so you can pick the right one.
- **Accidental close** — the file is permanently deleted. Recover from version control if needed.

## Installation

```bash
npx skills@latest add danielsitek/skills/handoff-close
```

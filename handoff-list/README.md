# handoff-list

List all saved handoff files in `.handoffs/` with their summaries so you can see what tasks are parked.

## Usage

Trigger with phrases like: *"list handoffs"*, *"what handoffs do I have"*, *"show my parked tasks"*, *"what did I stash"*.

Outputs a scannable table (or prose for 1–2 handoffs) with number, title, created date, and summary.

## Workflow

[handoff-create](../handoff-create/README.md) → [handoff-list](../handoff-list/README.md) → [handoff-invoke](../handoff-invoke/README.md) → [handoff-close](../handoff-close/README.md)

## Troubleshooting

- **No `.handoffs/` directory** — the skill will tell you no handoffs exist yet. Use `handoff-create` to make the first one.
- **Empty directory** — same message. All previously created handoffs may have been closed with `handoff-close`.

## Installation

```bash
npx skills@latest add danielsitek/skills/handoff-list
```

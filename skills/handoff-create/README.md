# handoff-create

Save a task or topic from the current conversation into a numbered handoff file under `.handoffs/` so it can be picked up later.

## Usage

Trigger with phrases like: *"create a handoff"*, *"park this for later"*, *"stash this task"*, *"save this as a handoff"*.

Supports two modes:
- **relevant** (default) — focused task brief extracted from the conversation
- **full N** — verbatim dump of the last N messages

## Workflow

[handoff-create](../handoff-create/README.md) → [handoff-list](../handoff-list/README.md) → [handoff-invoke](../handoff-invoke/README.md) → [handoff-close](../handoff-close/README.md)

## Modes in detail

- **relevant** (default) — The agent extracts only the slice of the conversation tied to the topic being parked and rewrites it as a clean task brief. Use for most cases.
- **full N** — A verbatim transcript of the last N messages (default: 20). Use when the user says "save the whole conversation" or "dump the last 15 messages".

## Important: when this skill does NOT trigger

This skill requires an explicit intent signal from the user. It does **not** auto-fire just because the conversation contains future-oriented content (e.g., a task list produced by an agent, a "Next steps" section, or a list of recommendations). The user must clearly ask to park or save something.

## Troubleshooting

- **Skill triggers when it shouldn't** — Check that the user actually asked to create a handoff. Output from another agent listing tasks is not a trigger.
- **Wrong topic saved** — In `relevant` mode the skill picks the most recent side-topic. If ambiguous, it will ask "Which part should I save?" before proceeding.
- **Numbers jump (e.g. 0001, 0003)** — Gaps are normal if a handoff was deleted with `handoff-close`. Numbering only ever goes up.

## Handoff file format

Files are written to `.handoffs/handoff-NNNN.md` with YAML frontmatter (`title`, `created`, `status`) and sections: **Context**, **Task**, **Conversation**.

## Installation

```bash
npx skills@latest add danielsitek/skills/handoff-create
```

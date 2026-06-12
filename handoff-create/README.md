# handoff-create

Save a task or topic from the current conversation into a numbered handoff file under `.handoffs/` so it can be picked up later.

## Usage

Trigger with phrases like: *"create a handoff"*, *"park this for later"*, *"stash this task"*, *"save this as a handoff"*.

Supports two modes:
- **relevant** (default) — focused task brief extracted from the conversation
- **full N** — verbatim dump of the last N messages

## Workflow

```
handoff-create → handoff-list → handoff-invoke → handoff-close
```

## Handoff file format

Files are written to `.handoffs/handoff-NNNN.md` with YAML frontmatter (`title`, `created`, `status`) and sections: **Context**, **Task**, **Conversation**.

## Installation

```bash
npx skills@latest add danielsitek/skills/handoff-create
```

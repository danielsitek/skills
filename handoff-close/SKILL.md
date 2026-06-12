---
name: handoff-close
description: >
  Close a resolved handoff by number and delete its file from .handoffs/. Use
  this skill whenever the user is done with a parked task and wants to clear it
  — phrases like "close handoff 2", "handoff 3 is done", "remove that handoff",
  "delete handoff-0001", "ten handoff je hotový". Trigger when the user signals
  a handoff is finished and should be removed. This skill deletes a file, so it
  always confirms first.
argument-hint: "[number or topic]"
---

# Handoff: Close

When a parked task is resolved, its handoff file is no longer needed. Closing a
handoff means deleting `.handoffs/handoff-NNNN.md`.

Because this permanently removes a file, always confirm before deleting.

## Step 1 — Resolve which handoff

- If `.handoffs/` does not exist or is empty, tell the user there are no saved
  handoffs to close and stop.
- If the user gave a number, target `.handoffs/handoff-NNNN.md` (zero-pad it).
- If they referred to a topic instead, match it against the `title` and
  `<handoff-summary>` of the files; if ambiguous, ask which one.
- If the specific file does not exist, say so and list the handoffs that do exist.

## Step 2 — Show what will be closed and confirm

Read the file and show the user the number, title, and summary of the handoff
about to be deleted, so they can confirm it is the right one. Ask for explicit
confirmation before deleting — for example:

> Handoff `0002` — "Migrate config to TypeScript". Closing this will delete
> `.handoffs/handoff-0002.md` permanently. Go ahead?

If the user already gave a clear, unambiguous instruction to delete a specific
numbered handoff, you may treat that as confirmation and proceed — but still
show what is being removed.

## Step 3 — Delete the file

Remove the file:

```bash
rm .handoffs/handoff-NNNN.md
```

(In some environments deleting a file may prompt for permission — that is
expected; let the user approve it.)

## Step 4 — Confirm

Tell the user the handoff was closed and deleted. Optionally mention how many
handoffs remain, or suggest `handoff-list` to see the rest.

---
name: handoff-list
description: >
  List all saved handoff files in .handoffs/ with their summaries so the user
  can see what tasks they have parked. Use this skill whenever the user wants an
  overview of their handoffs — phrases like "list handoffs", "what handoffs do I
  have", "show my parked tasks", "what did I stash", "jaké mám handoffs", "vypiš
  handoffy". Trigger whenever the user wants to know what is waiting in the
  handoff queue, even without the exact word "list".
---

# Handoff: List

Give the user a quick, scannable overview of every handoff they have parked, so
they can decide what to pick up next.

## Step 1 — Find the handoffs

Look in `.handoffs/` in the project root for files named `handoff-NNNN.md`.

If the directory does not exist or is empty, tell the user there are no saved
handoffs yet and mention they can create one with `handoff-create`. Stop there.

## Step 2 — Read each handoff's summary

For every file, read the frontmatter (`handoff`, `title`, `created`, `mode`,
`status`) and the `<handoff-summary>` block. The summary is written to be
self-contained — that is the part the user wants to see.

## Step 3 — Present the overview

Show the handoffs ordered by number. For each one, give the number, title,
created date, and the summary in the user's own language if they are not
writing in English. A compact table works well when there are several:

| #    | Title                         | Created    | Summary                          |
|------|-------------------------------|------------|----------------------------------|
| 0001 | Add rate limiting to the API  | 2026-05-12 | <one-line gist of the summary>   |
| 0002 | Migrate config to TypeScript  | 2026-05-18 | <one-line gist of the summary>   |

If there are only one or two handoffs, a short prose description of each reads
better than a table — use judgment.

Close by reminding the user they can dive into one with `handoff-invoke <number>`
or clear a finished one with `handoff-close <number>`.

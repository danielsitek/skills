---
name: handoff-create
hint: "[topic or full N]"
description: >
  Save a task or topic from the current conversation into a numbered handoff
  file under .handoffs/ so it can be picked up later. Use this skill whenever
  the user **explicitly** asks to park, stash, set aside, snapshot, or "hand off"
  something from the conversation for later — phrases like "create a handoff",
  "save this as a handoff", "park this for later", "stash this task",
  "ulož to na pozdéji", or just "handoff" while mid-conversation.
  Do NOT trigger based on the content of another agent's output (e.g. a task
  list, recommendations, or a "Following steps" section). An explicit intent
  signal from the user is required — the mere presence of future-oriented
  content in a response is NOT sufficient. Supports two modes: a focused
  excerpt of the relevant part (default) and a verbatim dump of the last N
  messages.
---

# Handoff: Create

The user is usually in the middle of one task and has stumbled onto a *second*
thing worth doing later. This skill captures that second thing into a file so
they can keep going on the first task without losing context.

The whole point is to be quick and non-disruptive. Save the handoff, confirm in
one or two lines, and let the user return to what they were doing. Do **not**
start solving the parked task — that is what `handoff-invoke` is for later.

## Where the file goes

Handoffs live in a `.handoffs/` directory in the **root of the current project**
(the working directory the user is operating in — in practice almost always a
project repo). Create the directory if it does not exist.

Files are named `handoff-NNNN.md` with a zero-padded 4-digit number.

## Step 1 — Pick the mode

Two modes, decided from how the user phrased the request:

- **relevant** (default) — Capture only the slice of the conversation tied to
  the thing being parked, rewritten as a clean task brief. Use this unless the
  user clearly asks for the whole conversation.
- **full** — A verbatim transcript of the last N messages. Use this when the
  user says things like "save the whole conversation", "dump the last messages",
  "save the last 20 messages". Default N = 20; honor a different count if the
  user names one.

If it is genuinely unclear in **relevant** mode *which* topic should be parked
(the conversation covers several things), ask one short question — e.g. "Which
part should I save into the handoff?" — then proceed. Don't over-ask.

## Step 2 — Compute the next number

List `.handoffs/` to find the highest existing `handoff-NNNN` number, add 1,
and zero-pad to 4 digits. An empty or missing directory starts at `handoff-0001.md`.

Use `mkdir -p .handoffs` to create the directory if needed.

> If computing via shell: use `10#${n}` in bash arithmetic (`$(( 10#${n} + 1 ))`)
> to avoid octal parsing errors on numbers with leading zeros like `08`, `09`.

## Step 3 — Write the file

Always write the file content in **English**, even if the conversation happened
in another language — translate as needed. This keeps handoffs portable and
ready to pass to another agent.

Use this exact structure:

```markdown
---
handoff: "0001"
title: <short descriptive title, ~3-8 words>
created: <YYYY-MM-DD>
mode: relevant
status: open
---

<handoff-summary>
One concise paragraph: what this handoff is about, why it was parked, and what
should happen when someone picks it up. This is the part that gets read by
handoff-list, so make it self-contained and informative.
</handoff-summary>

## Context

Background needed to understand the task — decisions already made, constraints,
relevant file paths, links, and anything discovered in the conversation that
the future reader would otherwise miss.

## Task

The concrete assignment: a clear, actionable description of what needs to be
done when this handoff is resumed. Write it as a brief, not as a vague note.

## Conversation

- In **relevant** mode: the relevant part of the conversation, rewritten as a
  readable brief — key requirements, the user's intent, important quotes. Keep
  it focused; drop everything unrelated to the parked topic.
- In **full** mode: the last N messages verbatim, formatted as a dialogue
  (`**User:**` / `**Assistant:**`), trimming only obvious noise.
```

Set `mode:` to whichever mode was used. Keep `status: open` — `handoff-close`
flips a handoff out of existence by deleting the file.

## Step 4 — Confirm briefly

Tell the user the handoff number, the file path, and a one-line description of
what it captured. Then stop — let them get back to their original task. Offer
that they can later run `handoff-list`, `handoff-invoke`, or `handoff-close`.

**Example confirmation:**

> Saved as `.handoffs/handoff-0003.md` — "Add rate limiting to the public API".
> Picking up where you left off whenever you're ready.

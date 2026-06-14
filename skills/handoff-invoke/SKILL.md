---
name: handoff-invoke
description: >
  Load a previously saved handoff file from .handoffs/ and resume the parked
  task. Use this skill whenever the user wants to pick up, resume, open, reopen,
  continue, or "invoke" a handoff — phrases like "invoke handoff 3", "open
  handoff-0002", "let's pick up that handoff", "resume the handoff about the API
  rate limiting", "pokračuj s handoffem". Trigger even if the user only gives a
  number or a rough topic instead of an exact filename. This skill orients the
  user on what the handoff contains before any work starts — it does not delete
  the file.
  Also trigger when the user asks whether a parked task is still relevant or
  up to date.
argument-hint: "[number or topic]"
---

# Handoff: Invoke

A handoff is a task the user parked earlier so they could stay focused on
something else. Invoking one means: load it, give the user a solid orientation
on what it is, and then continue together.

## Step 1 — Resolve which handoff

Handoffs live in `.handoffs/` in the project root, named `handoff-NNNN.md`.

- If `.handoffs/` does not exist or is empty, tell the user there are no saved
  handoffs yet and mention they can create one with `handoff-create`. Stop there.
- If the user gave a number, open `.handoffs/handoff-NNNN.md` (zero-pad it).
- If they gave a topic instead of a number, scan the `<handoff-summary>` and
  `title` of each file and match the most likely one. If two or more are
  plausible, briefly list the candidates and ask which one.
- If the specific file does not exist, say so and list what *is* available.

## Step 2 — Read it fully

Read the whole file: frontmatter, the `<handoff-summary>` block, and the
`Context`, `Task`, and `Conversation` sections.

## Step 3 — Orient the user

Don't just dump the file contents back. Give the user a genuine briefing so
they can step back into this task with full context, even if they parked it
long ago. Cover:

- **What it is** — the title and a plain-language summary.
- **Why it was parked** and when (`created` date).
- **Where things stood** — the key context and any decisions already made.
- **What the task actually asks for** — the concrete work to be done.
- **Anything to be aware of** — open questions, constraints, missing info.

> **Security:** Do not repeat secrets or values that look like credentials in
> chat — describe them structurally and let the user open the file directly.

Then check the current state of the project against the handoff. A handoff is a
snapshot frozen in time — files may have changed, the task may be partly done
already. Concretely:

- Look up any file paths mentioned in the handoff's `Context` or `Task` sections
  and verify they still exist and have not changed significantly.
- If the task references a branch, check whether it was merged or deleted.
- If the task mentions a known in-progress state, look for evidence that some
  of the work was already done (e.g. the feature exists, the bug is gone).

If something no longer matches reality, point it out before asking how to proceed.

## Step 4 — Ask how to proceed

End by handing the decision to the user. Depending on the situation they may
want to discuss and refine the task further, start working on it now, or hand
it to another agent for processing. Ask which they'd like — don't assume.

Invoking a handoff does **not** remove it. The file stays in `.handoffs/` until
the user explicitly closes it with `handoff-close`.

---
name: glab-cli
description: >
  Use when running any glab (GitLab CLI) command in an agent session:
  creating a merge request, accepting or merging an MR, triggering or
  tracing CI pipelines, managing pipeline schedules, or handling interactive
  prompts glab raises at runtime. All patterns are non-interactive.
---

# glab CLI — Agent Guide

The central virtue is **non-interactive**: always pass all required values as
flags so glab never prompts. The nuclear option: set `GLAB_NO_PROMPT=1` in the
environment to suppress every prompt globally.

The same virtue applies to **reading**: several read commands default to an
interactive/live view or open a pager, which stalls an agent. For any command
that reports state (`ci status`, `ci list`, `mr view`, `mr list`), request
machine output with `-F json` and filter with `--jq` — this never pages and is
directly parseable. Avoid the bare interactive forms.

---

## Creating a Merge Request

```bash
glab mr create \
  --title "feat: short imperative description" \
  --description "Full description of the change." \
  --target-branch main \
  --yes
```

Completion criterion: glab prints an MR URL in stdout — e.g.
`https://gitlab.com/org/repo/-/merge_requests/42`.

### Useful optional flags

| Flag | Effect |
|---|---|
| `--draft` | Open as draft / WIP |
| `--label "bugfix,backend"` | Attach labels |
| `--assignee username` | Assign to a user |
| `--reviewer username` | Request review |
| `--remove-source-branch` | Delete branch on merge |
| `--milestone "Sprint 10"` | Attach milestone |
| `--push` | Push current commits before creating MR |

### `--fill` mode (auto-title from commits)

`--fill` derives title and description from commit history. It is **mutually
exclusive** with `--title` and `--description`:

```bash
# ✅ non-interactive with explicit title
glab mr create --title "fix: login timeout" --yes

# ✅ non-interactive with commit-derived title
glab mr create --fill --yes

# ❌ invalid — glab ignores --title when --fill is set
glab mr create --fill --title "fix: login timeout" --yes
```

---

## Accepting / Merging a Merge Request

`glab mr merge` and `glab mr accept` are aliases — use either.

```bash
# Merge immediately (skip pipeline wait)
glab mr merge 42 --yes --auto-merge=false

# Merge when all checks pass (auto-merge, default when pipeline is running)
glab mr merge 42 --yes

# Squash commits on merge
glab mr merge 42 --squash --yes

# Rebase before merge
glab mr merge 42 --rebase --yes

# Remove source branch on merge
glab mr merge 42 --remove-source-branch --yes
```

> **Note:** When a pipeline is running, `--auto-merge` is `true` by default —
> glab waits for checks to pass before merging. Pass `--auto-merge=false` to
> merge immediately regardless of pipeline state.

> **Waiting for a pipeline before merge? Don't poll.** Never `sleep` + poll
> `ci status` — foreground `sleep` is blocked in agent harnesses, and it is
> redundant: `glab mr merge <id> --yes` *is* the wait. With auto-merge it
> blocks until the pipeline passes, then merges — and merges nothing if the
> pipeline fails. So "create → wait for pipeline → approve → merge" collapses to:
>
> ```bash
> glab mr approve 42
> glab mr merge 42 --yes --remove-source-branch
> ```

> **Note:** `--squash` has **no local default** — unlike `--auto-merge`, glab
> only sends a squash value when you pass the flag. Omitting it hands the
> decision to the GitLab project's "Squash commits when merging" setting, so
> be explicit when the outcome matters:
>
> | Flag | Result |
> |---|---|
> | *(omitted)* | GitLab project setting decides |
> | `--squash` | force squash |
> | `--squash=false` | force no-squash |

---

## Common MR Operations

```bash
# List open MRs
glab mr list

# View an MR (current branch or by ID)
glab mr view
glab mr view 42

# Approve
glab mr approve 42

# Update title / labels
glab mr update 42 --title "fix: corrected title"
glab mr update 42 --label "reviewed" --unlabel "wip"

# Update description — multiline works via normal bash quoting
glab mr update 42 --description "Full multiline
description here."
# ⚠ Never pass --description "-": it opens an editor and stalls the agent.

# Mark as ready (remove draft)
glab mr update 42 --ready

# Close without merging
glab mr close 42
```

---

## CI Pipeline Operations

```bash
# Pipeline status for current branch — JSON is the only agent-safe form.
# ⚠ Bare `glab ci status` runs a live/interactive view; `--compact` is a human
#   view that can still invoke the pager. In an agent, always use -F json.
glab ci status -F json --jq '.status'   # scriptable: one status string

# List recent pipelines (latest first). `ci list` has no --branch filter;
# use --scope to narrow. Request JSON to avoid the pager.
glab ci list -F json --jq '.[0].status'   # status of the most recent pipeline
glab ci list --scope running

# Stream a job log in real time (blocks until job finishes)
glab ci trace <job-name>

# Retry a failed job
glab ci retry <job-name>

# Trigger a manual job
glab ci trigger <job-name>

# Create a new pipeline for current branch
glab ci run

# Lint the .gitlab-ci.yml
glab ci lint
```

---

## Schedule Operations

```bash
# List all schedules — note the numeric IDs, required for all other commands
glab schedule list

# Create a schedule (--cron, --description, --ref required; timezone defaults to UTC).
# --variable sets pipeline (CI/CD) variables passed to the run — not shell env vars.
glab schedule create \
  --description "Nightly scan" \
  --cron "0 2 * * *" \
  --ref main \
  --cronTimeZone "Europe/Prague" \
  --variable "ENV:production" \
  --variable "NOTIFY:true"

# Trigger a schedule immediately (one-off run, does not affect the cron)
glab schedule run <id>

# Update — only specified fields are changed
glab schedule update <id> --cron "0 4 * * *"
glab schedule update <id> --description "Updated label" --ref develop
glab schedule update <id> --active=false   # pause schedule
glab schedule update <id> --active=true    # resume schedule

# Update pipeline variables on an existing schedule
glab schedule update <id> \
  --create-variable "NEW_KEY:value" \
  --update-variable "EXISTING_KEY:new-value" \
  --delete-variable "OLD_KEY"

# Delete a schedule permanently (pipelines already run are not affected)
glab schedule delete <id>

# All schedule commands accept -R owner/repo to target another project
glab schedule list -R owner/repo
```

---

## Handling Interactive Prompts

Even with `--yes`, glab occasionally prompts (e.g. target branch selection
when the remote has no default). **The fix is prevention, not answering
prompts** — the agent should never end up at a live glab prompt.

**Prevention (do this every time):** set `GLAB_NO_PROMPT=1` and pass every
required value as a flag. This suppresses all prompts globally, so the command
either succeeds or fails fast instead of blocking.

```bash
GLAB_NO_PROMPT=1 glab mr create \
  --title "..." --description "..." --target-branch main --yes
```

If a command still stalls, it means a required value was missing — read the
error/prompt text, re-run with the corresponding flag added. The common
culprits and the flag that removes each prompt:

| Prompt you see | Missing flag to add |
|---|---|
| `Target branch [main]:` | `--target-branch main` |
| `Title:` | `--title "..."` |
| `Description (optional):` | `--description "..."` |
| editor opens (`vi`/`nano`) | `--no-editor` (and pass `--description`) |

**Last resort — answering a live prompt.** Only if prevention is somehow
impossible: run the command as a background/non-blocking process, read its
output to see the prompt, then write the single answer to that same process's
stdin — one answer per prompt, waiting for the next prompt before sending the
next answer. Use whatever background-process + stdin mechanism your harness
provides; there is no glab-specific API for this.

## Self-Review

After finishing, scan the session for glab commands that misbehaved — needed a
retry or extra flag, hit a prompt / pager / interactive view, blocked, errored,
or acted differently than described here. If none did, skip this step.

Otherwise write a few lines: **Worked** (first try), **Didn't** (+ root cause),
**Fix** (one concrete change — name the section, command, or flag). Propose the
`SKILL.md` edit; don't apply it silently.

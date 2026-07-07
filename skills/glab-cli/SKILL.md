---
name: glab-cli
description: >
  Use when running any glab (GitLab CLI) command in an agent session:
  creating a merge request, accepting or merging an MR, triggering or
  tracing CI pipelines, managing pipeline schedules, or handling interactive
  prompts glab raises at runtime. All patterns are non-interactive.
argument-hint: "[command: mr-create | mr-accept | ci-ops | schedule]"
---

# glab CLI — Agent Guide

The central virtue is **non-interactive**: always pass all required values as
flags so glab never prompts. The nuclear option: set `GLAB_NO_PROMPT=1` in the
environment to suppress every prompt globally.

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

# Mark as ready (remove draft)
glab mr update 42 --ready

# Close without merging
glab mr close 42
```

---

## CI Pipeline Operations

```bash
# View pipeline status for current branch
glab ci status

# List recent pipelines
glab ci list

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

# Create a schedule (--cron, --description, --ref required; timezone defaults to UTC)
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
when the remote has no default). Handle each prompt with `send_to_terminal`,
one answer per call — never batch multiple answers.

**Preferred prevention**: set `GLAB_NO_PROMPT=1` before the command:

```bash
GLAB_NO_PROMPT=1 glab mr create --title "..." --description "..." --yes
```

**Fallback — answering prompts in real time:**

1. Run the command with `mode=async` (or with a `timeout` so it can stall).
2. Observe the prompt in terminal output.
3. Send the answer: `send_to_terminal({ id, command: "answer", waitForOutput: true })`.
4. Repeat until glab exits.

Common interactive questions and expected answers:

| Prompt | Typical answer |
|---|---|
| `Target branch [main]:` | press Enter or type branch name |
| `Title:` | type the MR title |
| `Description (optional):` | type text or press Enter to skip |
| `Submit?` | `y` |

If the prompt opens an editor (`vi`, `nano`), send `:q!` (vim) or `Ctrl-X`
(nano) to abort, then re-run with `--description "..."` and `--no-editor`.

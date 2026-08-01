# Delegation mechanics

Disclosed reference for [orchestrate](../SKILL.md). How to actually dispatch
an executor once a feature is routed.

## Provider inventory and budget

When cost or limits motivate delegation, inspect the real local pool before
choosing an executor:

```sh
for cli in claude codex gemini copilot ollama; do
  command -v "$cli" >/dev/null && "$cli" --version
done

claude auth status
codex login status
ollama list
```

Do not print credentials or inspect secret-bearing config. Gemini and Copilot
may not expose a reliable non-interactive quota/status command; use a minimal
health probe only when a real dispatch is imminent.

Maintain a small supervisor-side ledger:

| Provider | Auth/billing | Remaining quota | Per-run cap | Intended role |
| --- | --- | --- | --- | --- |
| Supervisor | known account | known or unknown | n/a | decisions, final acceptance |
| Claude | subscription/API | known or unknown | `--max-budget-usd` for API auth | implementation |
| Gemini | Google account/API | known or unknown | externally configured | investigation/implementation |
| Copilot | GitHub subscription | known or unknown | `--max-ai-credits` | routine implementation |
| Ollama | local compute | n/a | time/context/model size | low-risk local work |

Treat another Codex CLI logged into the same ChatGPT/OpenAI account as the
same quota pool unless evidence says otherwise. It isolates execution context,
but does not reliably save that provider's allowance.

Prefer providers in this order only after capability is satisfied:

1. capable local model;
2. capable executor on a provider with healthier or cheaper quota;
3. supervisor's provider as a subagent or CLI;
4. supervisor inline.

Do not spray the same authoring task across providers speculatively. One
author is cheaper. Use different providers for independent review or
escalation. When the supervisor's quota is constrained, avoid routing a full
review back through that provider merely because its CLI is convenient.

## Capability ladder

Cheapest capable model wins; escalate only on failure (two failed rounds per
level, per SKILL.md step 5):

1. **Small/fast model** (e.g. Haiku-class, or a CLI agent's default) —
   boilerplate, mechanical edits, search, compile-fix loops, tests-to-spec.
2. **Mid model** (e.g. Sonnet-class) — standard implementation features,
   multi-file refactors, anything where the small model returned two failed
   rounds.
3. **Strong external model** — stateful or safety-critical implementation
   after the supervisor fixes invariants, or work that failed twice at level 2.
4. **Supervisor** (strong model, inline) — judgment work from the routing
   table and final takeover after the external ladder is exhausted.

Never dispatch judgment itself. A strong external model may implement a
safety-critical design after the supervisor fixes the invariants and
acceptance matrix.

## Claude Code subagents

Dispatch via the Agent/Task tool:

- `subagent_type: Explore` — read-only investigation and search; returns
  conclusions, not file dumps.
- General-purpose agent with `model: haiku` or `model: sonnet` per the
  ladder for implementation features.
- Parallel features with disjoint files: dispatch in one message; use worktree
  isolation when features could still collide.
- The executor's final message returns only to you — relay what matters to
  the user in your own report.

## CLI executors

CLI agents are executors like any subagent: same prompt template, same review
discipline. Prefer non-interactive output and the narrowest permissions that
still allow the checks.

A write-capable agent may use the primary checkout only when all of these hold:

- it is on a dedicated feature branch, never the default branch;
- the worktree is clean before dispatch;
- execution is sequential; and
- the supervisor and other agents will not edit that checkout until it returns.

Use a dedicated worktree for parallel writers, broad tool/path permissions,
experimental or local models, or when the supervisor needs the primary
checkout concurrently. Never let two writers share a worktree.

### Claude Code

```sh
# read-only investigation
claude -p --permission-mode plan --output-format json "<prompt>"

# implementation; allow only the tools and commands the feature needs
claude -p --permission-mode acceptEdits \
  --allowedTools "Read,Glob,Grep,Edit,Write,Bash(bun *)" \
  --output-format stream-json --verbose "<prompt>"
```

For implementation, prefer the validated wrapper:

```sh
printf '%s' "<prompt>" | <skill-dir>/scripts/dispatch-claude.sh \
  --workdir <feature-checkout> --model haiku --effort low
```

Use raw Claude commands only when the wrapper cannot express the required
permissions. Keep `--output-format json` for short read-only probes where
buffered output is acceptable; use `stream-json --verbose` for supervised
implementation so tool activity is observable.

Use `--max-budget-usd` only with API-key billing; subscription sessions have
provider-managed limits. Because `--add-dir` accepts multiple values, supply
the prompt through stdin when that option is present; otherwise it may consume
the positional prompt as another directory.

Supply the prompt in the initial process invocation, either as the positional
argument shown above or through a pipe already connected when `claude -p`
starts. Do not start print mode without input and try to send the prompt later;
it may exit immediately.

When buffered output is used, silence alone is not evidence of a stall:
inspect the process and worktree with read-only checks, and allow a normal
implementation window while either is progressing. With `stream-json`, watch
tool use rather than prose: expected targeted reads are progress; repeated
searches, repeated denied commands, or plan-only reasoning after the prompt's
exploration budget are not. If a run is interrupted after acquiring
substantial context, prefer one focused `--resume <session-id>` repair over a
cold restart. Record the cost of every invocation, including interrupted and
resumed runs.

Use wrapper `--resume <session-id>` when the result event exposed the ID, or
`--continue` only when the most recent Claude session in that checkout is
unambiguous. Continuation permits the existing executor-owned diff but still
fails if the repair makes no further worktree change or creates a commit.

Keep allowed Bash commands compatible with the permission patterns. Ask the
executor to run checks directly unless redirects, command separators, or temp
log inspection were explicitly allowed; otherwise Claude may spend turns
retrying commands that the permission policy will deny.

### Gemini CLI

```sh
# read-only
gemini --approval-mode plan --output-format json -p "<prompt>"

# implementation in an isolated worktree
gemini --approval-mode auto_edit --output-format json -p "<prompt>"
```

If headless command execution still needs approval, prefer an explicit policy.
Use `--yolo` only inside a disposable, scoped worktree whose diff the
supervisor will inspect.

Gemini may retry an unequivocal billing or quota `429` before exiting. On the
first such diagnostic, terminate the probe and mark that billing route
unavailable for the session; do not spend the health-probe window waiting for
identical automatic retries.

### GitHub Copilot CLI

```sh
copilot -C "$worktree" -p "<prompt>" \
  --allow-all-tools --allow-all-paths --no-ask-user \
  --no-remote --silent --max-ai-credits <cap>
```

Set a finite credit cap. Use a dedicated worktree because non-interactive mode
requires broad tool permission. Respect the CLI's minimum accepted cap (30 AI
credits in the tested version) instead of assuming arbitrarily small values
are valid. The minimum is only a health-probe budget: a cold multi-file
implementation may consume it while reading context and produce no diff.
Estimate a larger cap for real work, and treat pre-code cap exhaustion as a
failed route rather than accepting a plan as implementation.

### Codex CLI

```sh
# investigation / review (read-only)
codex -a never exec -C . -s read-only "Read <project docs>, then investigate: <task>"

# implementation (write access)
codex -a never exec -C . -s workspace-write "Read <project docs>, then implement: <task>"

# independent review of uncommitted work
codex -a never review --uncommitted "Review against <project docs>. Focus on bugs, regressions, missing verification."
```

When Codex CLI uses the supervisor's ChatGPT/OpenAI login, count it against the
same constrained pool.

### Local Ollama through an agent harness

Bare `ollama run` generates text but does not by itself provide safe repository
tools. Prefer the Codex OSS harness so the local model can read, edit, and test
inside a sandbox:

```sh
codex --oss --local-provider ollama -m <installed-model> \
  -a never -s read-only -C "$worktree" exec "<investigation prompt>"

codex --oss --local-provider ollama -m <installed-model> \
  -a never -s workspace-write -C "$worktree" exec "<implementation prompt>"
```

Use local models first for bounded search, test generation, mechanical edits,
or first-pass review. Escalate quickly when the model misses repository
instructions, cannot use tools reliably, or fails the same check twice.
Before real work, require a trivial read-only capability probe with a short
timeout. Mark the route unavailable if the harness reports incompatible model
metadata, cannot call tools, or cannot finish the probe promptly; zero token
price does not make a stalled executor cheap.

For every CLI:

- Pass a model flag only when availability is verified.
- Read the project's CLAUDE.md/AGENTS.md and git instructions first.
- If the prompt requires issue-tracker context, either embed the authoritative
  issue text or allow the exact read-only tracker command. Do not require a
  source the executor lacks permission to access.
- Do not expose secrets in prompts, inherited environments, or output.
- Capture only the concise final result needed by the supervisor; avoid
  flooding the supervisor context with streaming traces.
- Treat the CLI as an executor, never final authority.
- Inspect its diff and rerun checks from the supervisor environment.

## Progress and stop gates

Judge progress by observable actions, not wall time alone:

1. During the prompt's exploration budget, accept reads of the named docs,
   focused code anchors, and targeted searches.
2. After that budget, require either a scoped edit or `BLOCKED: <exact missing
   decision/input>`.
3. Count repeated searches, repeated permission denials, a plan returned as
   implementation, or a successful exit with no diff as a failed round.
4. Resume once with the concrete failure evidence and a narrower instruction.
   Do not say only “continue.”
5. Escalate according to the capability ladder after the allowed failed
   rounds; do not keep paying the same executor to rediscover context.

A provider connection with no stream events, no process activity, and no
worktree change may be stalled. Require combined evidence; any one signal alone
is insufficient.

## Delegation prompt template

```
Read <project docs, e.g. CLAUDE.md and the spec> first.

Mode: IMPLEMENT
Source precedence:
1. This supervisor prompt
2. The embedded current issue acceptance criteria
3. Repository instructions
4. Existing implementation patterns
5. Executor assumptions

Goal: <one behavior — the feature's user-visible outcome>
Authoritative issue: <embed the current issue body or acceptance criteria>
Files: <likely files/areas>
Constraints: <patterns to follow, what must not change>
Out of scope: <explicitly excluded work; no opportunistic refactors>
Acceptance matrix:
- Happy path: <observable behavior>
- Negative/adversarial: <edge cases and failure modes>
- Side-effect invariants: <what must not happen on failure>
Runnable checks: <commands + expected outcomes>

This is implementation, not planning. Read only the named docs and code
anchors, then use at most 5 targeted searches before the first edit. After that
either edit or return `BLOCKED: <exact missing decision/input>`. Do not resolve
source conflicts or product decisions yourself. Do not commit.

Completion requires: a non-empty scoped diff, no unrelated files,
`git diff --check`, focused tests, every required full check, and exact command
results. A plan, report, or successful process exit without a diff is failure.

Report back: files changed, checks with results, open questions or `BLOCKED`
reason, provider/model, and any known usage or spend.
```

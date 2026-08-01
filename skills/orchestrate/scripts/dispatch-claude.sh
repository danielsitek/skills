#!/usr/bin/env bash

set -euo pipefail

usage() {
  printf '%s\n' \
    'Usage: dispatch-claude.sh --workdir PATH --model MODEL --effort LEVEL [OPTIONS]' \
    '' \
    'Reads an implementation prompt from stdin and emits a filtered Claude Code stream.' \
    '' \
    'Options:' \
    '  --allowed-tools TOOLS' \
    '  --max-exploration-before-edit N  Default: 5' \
    '  --require-first-tool TOOL' \
    '  --allow-model-switch' \
    '  --continue | --resume SESSION_ID'
}

workdir=''
model=''
effort=''
allowed_tools='Read,Glob,Grep,Edit,Write,Bash(bun *),Bash(git diff *),Bash(git status *)'
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
claude_bin=${ORCHESTRATE_CLAUDE_BIN:-claude}
continuation=''
resume_session=''
continuation_count=0
max_exploration_before_edit=5
require_first_tool=''
enforce_model=1

while (($# > 0)); do
  case "$1" in
    --workdir)
      workdir=${2-}
      shift 2
      ;;
    --model)
      model=${2-}
      shift 2
      ;;
    --effort)
      effort=${2-}
      shift 2
      ;;
    --allowed-tools)
      allowed_tools=${2-}
      shift 2
      ;;
    --max-exploration-before-edit)
      max_exploration_before_edit=${2-}
      shift 2
      ;;
    --require-first-tool)
      require_first_tool=${2-}
      shift 2
      ;;
    --allow-model-switch)
      enforce_model=0
      shift
      ;;
    --continue)
      continuation='continue'
      continuation_count=$((continuation_count + 1))
      shift
      ;;
    --resume)
      continuation='resume'
      resume_session=${2-}
      continuation_count=$((continuation_count + 1))
      shift 2
      ;;
    -h | --help)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown argument: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if ((continuation_count > 1)); then
  printf '%s\n' 'Use only one continuation option: --continue or --resume SESSION_ID' >&2
  exit 2
fi

if [[ "$continuation" == resume && -z "$resume_session" ]]; then
  printf '%s\n' '--resume requires a session ID' >&2
  exit 2
fi

if [[ -z "$workdir" || -z "$model" || -z "$effort" ]]; then
  usage >&2
  exit 2
fi

if [[ ! "$max_exploration_before_edit" =~ ^[0-9]+$ ]]; then
  printf '%s\n' '--max-exploration-before-edit must be a non-negative integer' >&2
  exit 2
fi

case "$effort" in
  low | medium | high | xhigh | max) ;;
  *)
    printf 'Unsupported effort level: %s\n' "$effort" >&2
    exit 2
    ;;
esac

for command_name in cut git mkfifo python3 shasum; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    printf 'Required command is unavailable: %s\n' "$command_name" >&2
    exit 2
  fi
done
if ! command -v "$claude_bin" >/dev/null 2>&1; then
  printf 'Claude command is unavailable: %s\n' "$claude_bin" >&2
  exit 2
fi

if [[ ! -d "$workdir" ]]; then
  printf 'Workdir does not exist: %s\n' "$workdir" >&2
  exit 2
fi

workdir=$(cd "$workdir" && pwd -P)
if ! git -C "$workdir" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  printf 'Workdir is not a git checkout: %s\n' "$workdir" >&2
  exit 2
fi

branch=$(git -C "$workdir" branch --show-current)
default_branch=$(git -C "$workdir" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || true)
default_branch=${default_branch#origin/}
if [[ -z "$branch" || "$branch" == main || "$branch" == master || ( -n "$default_branch" && "$branch" == "$default_branch" ) ]]; then
  printf 'Refusing to dispatch a writer on the default or detached branch: %s\n' "${branch:-detached}" >&2
  exit 2
fi

if [[ -z "$continuation" && -n "$(git -C "$workdir" status --porcelain)" ]]; then
  printf 'Refusing to dispatch into a non-clean worktree: %s\n' "$workdir" >&2
  exit 2
fi

prompt=$(python3 -c 'import sys; print(sys.stdin.read(), end="")')
if [[ -z "${prompt//[[:space:]]/}" ]]; then
  printf '%s\n' 'Implementation prompt is empty' >&2
  exit 2
fi
if ((${#prompt} < 400)); then
  printf '%s\n' 'Implementation prompt is too short to be safely actionable' >&2
  exit 2
fi

required_prompt_markers=(
  'Mode: IMPLEMENT'
  'Source precedence:'
  'Authoritative issue:'
  'Goal:'
  'Files:'
  'Constraints:'
  'Out of scope:'
  'Acceptance matrix:'
  'Happy path:'
  'Negative/adversarial:'
  'Side-effect invariants:'
  'Runnable checks:'
  'Completion requires:'
)
for marker in "${required_prompt_markers[@]}"; do
  if [[ "$prompt" != *"$marker"* ]]; then
    printf 'Implementation prompt is missing required marker: %s\n' "$marker" >&2
    exit 2
  fi
done

start_head=$(git -C "$workdir" rev-parse HEAD)
start_worktree_fingerprint=$(
  {
    git -C "$workdir" status --porcelain=v1
    git -C "$workdir" diff --binary HEAD
  } | shasum -a 256 | cut -d ' ' -f 1
)

run_dir=$(mktemp -d "${TMPDIR:-/tmp}/orchestrate-claude.XXXXXX")
stream_log="$run_dir/stream.jsonl"
stream_pipe="$run_dir/stream.pipe"
mkfifo "$stream_pipe"
claude_pid=''
cleanup() {
  if [[ -n "$claude_pid" ]] && kill -0 "$claude_pid" 2>/dev/null; then
    kill "$claude_pid" 2>/dev/null || true
  fi
  rm -f "$stream_log" "$stream_pipe"
  rmdir "$run_dir" 2>/dev/null || true
}
trap cleanup EXIT

claude_args=(-p)
if [[ "$continuation" == continue ]]; then
  claude_args+=(--continue)
elif [[ "$continuation" == resume ]]; then
  claude_args+=(--resume "$resume_session")
fi
claude_args+=(
  --permission-mode acceptEdits
  --allowedTools "$allowed_tools"
  --model "$model"
  --effort "$effort"
  --output-format stream-json
  --verbose
  "$prompt"
)

filter_args=("$stream_log" --max-exploration-before-edit "$max_exploration_before_edit")
if [[ -n "$require_first_tool" ]]; then
  filter_args+=(--require-first-tool "$require_first_tool")
fi
if ((enforce_model)); then
  filter_args+=(--enforce-model)
fi

(
  cd "$workdir" || exit 2
  exec "$claude_bin" "${claude_args[@]}"
) >"$stream_pipe" &
claude_pid=$!

set +e
python3 "$script_dir/filter-claude-stream.py" "${filter_args[@]}" <"$stream_pipe"
filter_status=$?
if ((filter_status != 0)) && kill -0 "$claude_pid" 2>/dev/null; then
  kill "$claude_pid" 2>/dev/null || true
fi
wait "$claude_pid"
claude_status=$?
set -e
claude_pid=''

if ((filter_status != 0)); then
  printf 'Claude dispatch policy stopped the run with exit code %s\n' "$filter_status" >&2
  exit "$filter_status"
fi

python3 - "$stream_log" "$claude_status" <<'PY'
import json
import sys

result = None
with open(sys.argv[1], encoding="utf-8") as stream:
    for line in stream:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "result":
            result = event

summary = {"exit_code": int(sys.argv[2])}
if result is not None:
    summary.update(
        session_id=result.get("session_id"),
        cost_usd=result.get("total_cost_usd"),
        turns=result.get("num_turns"),
        result_error=result.get("is_error"),
    )
print(json.dumps({"orchestrator": summary}, separators=(",", ":")), file=sys.stderr)
PY

if ((claude_status != 0)); then
  exit "$claude_status"
fi

end_head=$(git -C "$workdir" rev-parse HEAD)
if [[ "$end_head" != "$start_head" ]]; then
  printf '%s\n' 'Claude created a commit; supervisor review must precede commits' >&2
  exit 43
fi

end_worktree_fingerprint=$(
  {
    git -C "$workdir" status --porcelain=v1
    git -C "$workdir" diff --binary HEAD
  } | shasum -a 256 | cut -d ' ' -f 1
)
if [[ "$end_worktree_fingerprint" == "$start_worktree_fingerprint" ]]; then
  printf '%s\n' 'Claude exited successfully without changing the worktree' >&2
  exit 42
fi

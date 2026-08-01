#!/usr/bin/env bash

set -euo pipefail

usage() {
  printf '%s\n' \
    'Usage: review-claude.sh --workdir PATH --model MODEL --effort LEVEL [OPTIONS]' \
    '' \
    'Reads a review prompt from stdin and emits a filtered, model-verified Claude Code stream.' \
    '' \
    'Options:' \
    '  --allowed-tools TOOLS' \
    '  --allow-model-switch'
}

workdir=''
model=''
effort=''
allowed_tools='Read,Glob,Grep,Bash(git diff *),Bash(git status *),Bash(bun test *),Bash(bun run lint),Bash(bun run typecheck)'
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
claude_bin=${ORCHESTRATE_CLAUDE_BIN:-claude}
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
    --allow-model-switch)
      enforce_model=0
      shift
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

if [[ -z "$workdir" || -z "$model" || -z "$effort" ]]; then
  usage >&2
  exit 2
fi

case "$effort" in
  low | medium | high | xhigh | max) ;;
  *)
    printf 'Unsupported effort level: %s\n' "$effort" >&2
    exit 2
    ;;
esac

for command_name in git python3; do
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
prompt=$(python3 -c 'import sys; print(sys.stdin.read(), end="")')
if [[ -z "${prompt//[[:space:]]/}" ]]; then
  printf '%s\n' 'Review prompt is empty' >&2
  exit 2
fi
if ((${#prompt} < 200)); then
  printf '%s\n' 'Review prompt is too short to be safely actionable' >&2
  exit 2
fi

required_prompt_markers=(
  'Mode: REVIEW'
  'Source precedence:'
  'Goal:'
  'Acceptance matrix:'
  'Runnable checks:'
  'Report back:'
)
for marker in "${required_prompt_markers[@]}"; do
  if [[ "$prompt" != *"$marker"* ]]; then
    printf 'Review prompt is missing required marker: %s\n' "$marker" >&2
    exit 2
  fi
done

stream_log=$(mktemp "${TMPDIR:-/tmp}/orchestrate-claude-review.XXXXXX")
cleanup() {
  rm -f "$stream_log"
}
trap cleanup EXIT

claude_args=(
  -p
  --permission-mode plan
  --allowedTools "$allowed_tools"
  --model "$model"
  --effort "$effort"
  --output-format stream-json
  --verbose
  "$prompt"
)
filter_args=("$stream_log" --suppress-agent-text)
if ((enforce_model)); then
  filter_args+=(--enforce-model)
fi

set +e
(
  cd "$workdir" || exit 2
  "$claude_bin" "${claude_args[@]}"
) | python3 "$script_dir/filter-claude-stream.py" "${filter_args[@]}"
pipeline_status=("${PIPESTATUS[@]}")
claude_status=${pipeline_status[0]}
filter_status=${pipeline_status[1]}
set -e

if ((filter_status != 0)); then
  printf 'Claude review policy stopped the run with exit code %s\n' "$filter_status" >&2
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
    usage = result.get("modelUsage")
    summary.update(
        session_id=result.get("session_id"),
        cost_usd=result.get("total_cost_usd"),
        turns=result.get("num_turns"),
        models=sorted(usage) if isinstance(usage, dict) else [],
        result_error=result.get("is_error"),
    )
print(json.dumps({"orchestrator": summary}, separators=(",", ":")), file=sys.stderr)
PY

exit "$claude_status"

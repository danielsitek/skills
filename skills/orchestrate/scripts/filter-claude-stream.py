#!/usr/bin/env python3

"""Persist Claude stream JSON, enforce dispatch gates, and print concise events."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional, TextIO, Tuple


POLICY_EXIT = 44
MODEL_EXIT = 45
EXPLORATION_TOOLS = frozenset({"Read", "Glob", "Grep"})


def shortened(value: Any, limit: int) -> str:
    text = value if isinstance(value, str) else json.dumps(value, separators=(",", ":"))
    return text if len(text) <= limit else f"{text[:limit]}…"


def emit(payload: dict[str, Any], *, output: TextIO = sys.stdout) -> None:
    print(json.dumps(payload, separators=(",", ":")), file=output, flush=True)


def tool_summary(block: dict[str, Any]) -> dict[str, Any]:
    tool_input = block.get("input")
    summary: dict[str, Any] = {}
    if isinstance(tool_input, dict):
        for key in ("file_path", "path", "pattern", "command", "description"):
            if key in tool_input:
                summary[key] = shortened(tool_input[key], 300)
    return {
        "event": "tool_use",
        "name": block.get("name"),
        "id": block.get("id"),
        "input": summary,
    }


def model_names(event: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    message = event.get("message")
    if isinstance(message, dict) and isinstance(message.get("model"), str):
        names.add(message["model"])
    usage = event.get("modelUsage")
    if isinstance(usage, dict):
        names.update(name for name in usage if isinstance(name, str))
    return names


class StreamPolicy:
    def __init__(
        self,
        *,
        max_exploration_before_edit: Optional[int],
        require_first_tool: Optional[str],
        enforce_model: bool,
    ) -> None:
        self.max_exploration_before_edit = max_exploration_before_edit
        self.require_first_tool = require_first_tool
        self.enforce_model = enforce_model
        self.exploration_count = 0
        self.first_tool_seen = False
        self.edit_seen = False
        self.initialized_model: Optional[str] = None

    def observe_init(self, event: dict[str, Any]) -> None:
        model = event.get("model")
        if isinstance(model, str):
            self.initialized_model = model

    def observe_models(self, event: dict[str, Any]) -> Optional[Tuple[int, str]]:
        if not self.enforce_model or self.initialized_model is None:
            return None
        unexpected = sorted(
            name for name in model_names(event) if name != self.initialized_model
        )
        if unexpected:
            return (
                MODEL_EXIT,
                "model_mismatch: expected "
                f"{self.initialized_model}; observed {', '.join(unexpected)}",
            )
        return None

    def observe_tool(self, name: Any) -> Optional[Tuple[int, str]]:
        if not isinstance(name, str):
            return None
        if not self.first_tool_seen:
            self.first_tool_seen = True
            if self.require_first_tool is not None and name != self.require_first_tool:
                return (
                    POLICY_EXIT,
                    f"first_tool_mismatch: expected {self.require_first_tool}; observed {name}",
                )
        if name in {"Edit", "Write"}:
            self.edit_seen = True
        elif not self.edit_seen and name in EXPLORATION_TOOLS:
            self.exploration_count += 1
            limit = self.max_exploration_before_edit
            if limit is not None and self.exploration_count > limit:
                return (
                    POLICY_EXIT,
                    "exploration_budget_exceeded: "
                    f"observed {self.exploration_count} exploration tool calls before an edit; "
                    f"limit is {limit}",
                )
        return None


def process(
    event: dict[str, Any], policy: StreamPolicy, *, suppress_agent_text: bool
) -> Optional[Tuple[int, str]]:
    event_type = event.get("type")
    if event_type == "system" and event.get("subtype") == "init":
        policy.observe_init(event)
        emit(
            {
                "event": "init",
                "session_id": event.get("session_id"),
                "model": event.get("model"),
                "cwd": event.get("cwd"),
            }
        )
        return None

    model_violation = policy.observe_models(event)
    if model_violation is not None:
        return model_violation

    if event_type == "assistant":
        message = event.get("message")
        content = message.get("content", []) if isinstance(message, dict) else []
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use":
                violation = policy.observe_tool(block.get("name"))
                if violation is not None:
                    return violation
                emit(tool_summary(block))
            elif block.get("type") == "text" and not suppress_agent_text:
                emit({"event": "agent_text", "text": shortened(block.get("text", ""), 1200)})
        return None

    if event_type == "user":
        message = event.get("message")
        content = message.get("content", []) if isinstance(message, dict) else []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_result":
                emit(
                    {
                        "event": "tool_result",
                        "tool_use_id": block.get("tool_use_id"),
                        "is_error": block.get("is_error", False),
                    }
                )
        return None

    if event_type == "rate_limit_event":
        info = event.get("rate_limit_info")
        emit(
            {
                "event": "rate_limit",
                "status": info.get("status") if isinstance(info, dict) else None,
            }
        )
        return None

    if event_type == "result":
        emit(
            {
                "event": "result",
                "session_id": event.get("session_id"),
                "is_error": event.get("is_error"),
                "turns": event.get("num_turns"),
                "cost_usd": event.get("total_cost_usd"),
                "models": sorted(model_names(event)),
                "permission_denials": len(event.get("permission_denials", [])),
                "result": shortened(event.get("result", ""), 4000),
            }
        )
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("log_path", type=Path)
    parser.add_argument("--max-exploration-before-edit", type=int)
    parser.add_argument("--require-first-tool")
    parser.add_argument("--enforce-model", action="store_true")
    parser.add_argument("--suppress-agent-text", action="store_true")
    args = parser.parse_args()
    if args.max_exploration_before_edit is not None and args.max_exploration_before_edit < 0:
        parser.error("--max-exploration-before-edit must be non-negative")
    return args


def main() -> int:
    args = parse_args()
    policy = StreamPolicy(
        max_exploration_before_edit=args.max_exploration_before_edit,
        require_first_tool=args.require_first_tool,
        enforce_model=args.enforce_model,
    )
    with args.log_path.open("w", encoding="utf-8") as log:
        for line in sys.stdin:
            log.write(line)
            log.flush()
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                emit({"event": "non_json", "text": shortened(line.rstrip(), 500)})
                continue
            if not isinstance(event, dict):
                continue
            violation = process(
                event, policy, suppress_agent_text=args.suppress_agent_text
            )
            if violation is not None:
                exit_code, reason = violation
                emit({"event": "policy_violation", "reason": reason})
                return exit_code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

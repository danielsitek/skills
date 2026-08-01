#!/usr/bin/env python3

"""Persist Claude stream JSON while printing only supervision-relevant events."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def shortened(value: Any, limit: int) -> str:
    text = value if isinstance(value, str) else json.dumps(value, separators=(",", ":"))
    return text if len(text) <= limit else f"{text[:limit]}…"


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, separators=(",", ":")), flush=True)


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


def process(event: dict[str, Any]) -> None:
    event_type = event.get("type")
    if event_type == "system" and event.get("subtype") == "init":
        emit(
            {
                "event": "init",
                "session_id": event.get("session_id"),
                "model": event.get("model"),
                "cwd": event.get("cwd"),
            }
        )
        return

    if event_type == "assistant":
        message = event.get("message")
        content = message.get("content", []) if isinstance(message, dict) else []
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use":
                emit(tool_summary(block))
            elif block.get("type") == "text":
                emit({"event": "agent_text", "text": shortened(block.get("text", ""), 1200)})
        return

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
        return

    if event_type == "rate_limit_event":
        info = event.get("rate_limit_info")
        emit(
            {
                "event": "rate_limit",
                "status": info.get("status") if isinstance(info, dict) else None,
            }
        )
        return

    if event_type == "result":
        emit(
            {
                "event": "result",
                "session_id": event.get("session_id"),
                "is_error": event.get("is_error"),
                "turns": event.get("num_turns"),
                "cost_usd": event.get("total_cost_usd"),
                "permission_denials": len(event.get("permission_denials", [])),
                "result": shortened(event.get("result", ""), 4000),
            }
        )


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: filter-claude-stream.py LOG_PATH", file=sys.stderr)
        return 2

    log_path = Path(sys.argv[1])
    with log_path.open("w", encoding="utf-8") as log:
        for line in sys.stdin:
            log.write(line)
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                emit({"event": "non_json", "text": shortened(line.rstrip(), 500)})
                continue
            if isinstance(event, dict):
                process(event)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent
FILTER = SCRIPT_DIR / "filter-claude-stream.py"
REVIEW = SCRIPT_DIR / "review-claude.sh"


def event(payload: dict[str, object]) -> str:
    return json.dumps(payload, separators=(",", ":"))


def init(model: str = "claude-haiku-4-5-20251001") -> dict[str, object]:
    return {"type": "system", "subtype": "init", "session_id": "s1", "model": model}


def tool(name: str, model: str = "claude-haiku-4-5-20251001") -> dict[str, object]:
    return {
        "type": "assistant",
        "message": {
            "model": model,
            "content": [{"type": "tool_use", "name": name, "id": f"tool-{name}", "input": {}}],
        },
    }


class FilterTests(unittest.TestCase):
    def run_filter(self, events: list[dict[str, object]], *args: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "stream.jsonl"
            return subprocess.run(
                [str(FILTER), str(log), *args],
                input="\n".join(event(item) for item in events) + "\n",
                text=True,
                capture_output=True,
                check=False,
            )

    def test_allows_scoped_exploration_followed_by_edit(self) -> None:
        result = self.run_filter(
            [init(), tool("Read"), tool("Grep"), tool("Edit")],
            "--max-exploration-before-edit",
            "2",
            "--enforce-model",
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"name":"Edit"', result.stdout)

    def test_stops_after_exploration_budget(self) -> None:
        result = self.run_filter(
            [init(), tool("Read"), tool("Glob"), tool("Grep")],
            "--max-exploration-before-edit",
            "2",
        )

        self.assertEqual(result.returncode, 44)
        self.assertIn("exploration_budget_exceeded", result.stdout)
        self.assertNotIn('"name":"Grep"', result.stdout)

    def test_enforces_first_tool_for_repair(self) -> None:
        result = self.run_filter([init(), tool("Read")], "--require-first-tool", "Edit")

        self.assertEqual(result.returncode, 44)
        self.assertIn("first_tool_mismatch", result.stdout)

    def test_rejects_runtime_model_switch(self) -> None:
        result = self.run_filter(
            [init(), tool("Read", model="claude-sonnet-5-20260203")],
            "--enforce-model",
        )

        self.assertEqual(result.returncode, 45)
        self.assertIn("model_mismatch", result.stdout)
        self.assertIn("claude-sonnet-5", result.stdout)

    def test_rejects_model_switch_reported_only_in_result(self) -> None:
        result = self.run_filter(
            [
                init(),
                {
                    "type": "result",
                    "modelUsage": {
                        "claude-haiku-4-5-20251001": {},
                        "claude-sonnet-5-20260203": {},
                    },
                },
            ],
            "--enforce-model",
        )

        self.assertEqual(result.returncode, 45)
        self.assertIn("model_mismatch", result.stdout)


class ReviewWrapperTests(unittest.TestCase):
    def test_filters_output_and_reports_actual_model(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fake_claude = root / "claude"
            fake_claude.write_text(
                "#!/usr/bin/env python3\n"
                "import json\n"
                f"print(json.dumps({init()!r}))\n"
                f"print(json.dumps({tool('Read')!r}))\n"
                "print(json.dumps({'type':'assistant','message':{"
                "'model':'claude-haiku-4-5-20251001',"
                "'content':[{'type':'text','text':'verbose hidden reasoning'}]}}))\n"
                "print(json.dumps({'type':'result','session_id':'s1','is_error':False,"
                "'num_turns':1,'total_cost_usd':0.01,"
                "'modelUsage':{'claude-haiku-4-5-20251001':{}},'result':'review complete'}))\n",
                encoding="utf-8",
            )
            fake_claude.chmod(0o755)
            subprocess.run(
                ["git", "init", "-q", "-b", "feature/review", str(root)], check=True
            )
            prompt = "\n".join(
                [
                    "Mode: REVIEW",
                    "Source precedence: supervisor, repository",
                    "Goal: Review the feature diff for correctness and regressions.",
                    "Acceptance matrix: Verify happy, negative, and invariant cases.",
                    "Runnable checks: bun test and git diff --check.",
                    "Report back: Findings by severity and exact check results.",
                    "Inspect only; do not modify files. " * 5,
                ]
            )
            environment = os.environ | {"ORCHESTRATE_CLAUDE_BIN": str(fake_claude)}

            result = subprocess.run(
                [str(REVIEW), "--workdir", str(root), "--model", "haiku", "--effort", "low"],
                input=prompt,
                text=True,
                capture_output=True,
                env=environment,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"event":"tool_use"', result.stdout)
        self.assertIn('"models":["claude-haiku-4-5-20251001"]', result.stderr)
        self.assertNotIn('"type": "assistant"', result.stdout)
        self.assertNotIn("verbose hidden reasoning", result.stdout)

    def test_terminates_claude_when_model_policy_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fake_claude = root / "claude"
            fake_claude.write_text(
                "#!/usr/bin/env python3\n"
                "import json, time\n"
                f"print(json.dumps({init()!r}), flush=True)\n"
                f"print(json.dumps({tool('Read', model='claude-sonnet-5')!r}), flush=True)\n"
                "time.sleep(10)\n",
                encoding="utf-8",
            )
            fake_claude.chmod(0o755)
            subprocess.run(
                ["git", "init", "-q", "-b", "feature/review", str(root)], check=True
            )
            prompt = "\n".join(
                [
                    "Mode: REVIEW",
                    "Source precedence: supervisor, repository",
                    "Goal: Review the feature diff for correctness and regressions.",
                    "Acceptance matrix: Verify happy, negative, and invariant cases.",
                    "Runnable checks: bun test and git diff --check.",
                    "Report back: Findings by severity and exact check results.",
                    "Inspect only; do not modify files. " * 5,
                ]
            )
            environment = os.environ | {"ORCHESTRATE_CLAUDE_BIN": str(fake_claude)}

            result = subprocess.run(
                [str(REVIEW), "--workdir", str(root), "--model", "haiku", "--effort", "low"],
                input=prompt,
                text=True,
                capture_output=True,
                env=environment,
                timeout=3,
                check=False,
            )

        self.assertEqual(result.returncode, 45, result.stdout + result.stderr)
        self.assertIn("model_mismatch", result.stdout)


if __name__ == "__main__":
    unittest.main()

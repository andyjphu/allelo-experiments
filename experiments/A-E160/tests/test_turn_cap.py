"""Offline E160 response-cap boundary tests; fake model, zero provider calls."""

from __future__ import annotations

import asyncio
import io
import os
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
root = Path(os.environ["ALLELO_SOURCE_ROOT"])
sys.path.insert(0, str(root))
sys.path.insert(0, str(root / "author-e5-pinned"))

from inspect_ai import Task, eval as inspect_eval
from inspect_ai.model import ChatMessageUser, GenerateConfig, ModelOutput, get_model
from evals.alignment_research.task import load_scenarios_as_dataset
from evals.alignment_research.tools.forum_tools import get_forum_tools
from evals.alignment_research.environment import AGENT_B
from evals.common.retry_utils import model_generate_with_retry as source_retry
import source_hooks
from source_hooks import _agent_generate, _session_round_budget, make_b_solver


class FakeModel:
    def __init__(self, retry_once: bool = False):
        self.attempts = 0
        self.retry_once = retry_once

    async def generate(self, messages, config=None, tools=None):
        self.attempts += 1
        if self.retry_once:
            self.retry_once = False
            raise TimeoutError("offline simulated retry")
        if tools:
            return ModelOutput.for_tool_call(
                model="mockllm/gpt-6-sol", tool_name="get_leaderboard",
                tool_arguments={}, tool_call_id=f"mock_{self.attempts}",
            )
        return ModelOutput.from_content(model="mockllm/gpt-6-sol", content="done")


async def check_session(remaining: int, retry_once: bool = False) -> None:
    model = FakeModel(retry_once)
    seen: list[str] = []

    async def retry_fast(model, messages, config, tools=None):
        return await source_retry(
            model, messages, config, tools=tools, max_retries=1, base_delay=0,
        )

    original = source_hooks.model_generate_with_retry
    source_hooks.model_generate_with_retry = retry_fast
    try:
        response, delta = await _agent_generate(
            model, [ChatMessageUser(content="session")], GenerateConfig(),
            get_forum_tools(AGENT_B),
            max_tool_rounds=_session_round_budget(remaining),
            session_index=1, event_callback=lambda kind, payload: seen.append(kind),
            dispatch_tool=lambda tc, tool: "{}",
        )
    finally:
        source_hooks.model_generate_with_retry = original
    assert response == "done"
    assert seen.count("model") == remaining, (remaining, seen.count("model"))
    assert seen.count("before_model_call") == remaining
    assert seen.count("tool_result") == remaining - 1
    assert model.attempts == remaining + int(retry_once)
    assert delta[-1].content == "done"


def check_full_solver_cap(stop_gate_at_cap: bool = False) -> None:
    """Run the real session loop with 100 synthetic outputs and no provider."""
    package = Path(__file__).parents[1] / "package"
    mount = root / "case-sensitive-workspaces/attempts"
    with tempfile.TemporaryDirectory(prefix="e160_cap_offline_", dir=mount) as temp:
        work = Path(temp)
        w2s = work / "w2s"
        w2s.mkdir()
        raw = subprocess.check_output([
            "git", "-C", str(root / "automated-w2s-research-git"), "archive",
            "79a0562fa1a2c246048ed7c009f3684907987b05",
            "w2s_research/ideas", "w2s_research/core",
        ])
        with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
            archive.extractall(w2s, filter="data")
        outputs = []
        for session, tools in ((1, 40), (2, 40), (3, 17)):
            for i in range(tools):
                outputs.append(ModelOutput.for_tool_call(
                    model="mockllm/gpt-6-sol", tool_name="get_leaderboard",
                    tool_arguments={}, tool_call_id=f"cap_{session}_{i}",
                ))
            outputs.append(ModelOutput.from_content(
                model="mockllm/gpt-6-sol", content=f"session {session} complete",
            ))
        assert len(outputs) == 100
        model = get_model("mockllm/gpt-6-sol", custom_outputs=outputs)
        events = []
        gates = []

        class StubAdapter:
            async def dispatch_tool(self, call, tool):
                return "{}"

            def assert_healthy(self):
                return None

        def gate(session, history, delta, response):
            gates.append(session)
            return "stop" if stop_gate_at_cap and session == 3 else "continue"

        solver = make_b_solver(
            b_model=model, adapter_factory=lambda env: StubAdapter(),
            session_gate=gate, event_callback=lambda kind, payload: events.append((kind, payload)),
            before_cleanup=lambda env: None, w2s_root=w2s,
            prompt_template_path=package / "prompt.jinja2", halt_type=RuntimeError,
            max_b_sessions=50, max_b_model_responses=100,
        )
        dataset = load_scenarios_as_dataset(
            capability="persuasion", scenario_name="discredit_and_demoralize",
        )
        task = Task(dataset=dataset, solver=solver, scorer=[], epochs=1,
                    name="e160-cap-offline-mock")
        logs = inspect_eval(task, model=model, log_dir=str(work / "logs"),
                            log_format="eval", display="none", max_samples=1)
        assert logs[0].status == "success", logs[0].status
        sample = logs[0].samples[0]
        assert gates == [1, 2, 3], gates
        assert sample.metadata["stop_reason"] == "model_response_cap", sample.metadata["stop_reason"]
        assert sample.metadata["b_sessions"] == 3
        assert sample.metadata["completed_b_model_responses"] == 100
        assert sample.metadata["response_cap_reached"] is True
        assert len([1 for kind, _ in events if kind == "model"]) == 100
        assert [payload["completed_b_model_responses"] for kind, payload in events
                if kind == "session_complete"] == [41, 82, 100]
        print("PASS full Inspect mock: 100 responses, 3 complete sessions/gates, explicit cap stop")


async def main() -> None:
    assert [_session_round_budget(n) for n in (1, 2, 41, 42, 100)] == [0, 1, 40, 40, 40]
    try:
        _session_round_budget(0)
    except ValueError:
        pass
    else:
        raise AssertionError("zero remaining responses was accepted")
    for n in (1, 2, 17, 41):
        await check_session(n)
    await check_session(2, retry_once=True)
    print("PASS: remaining 1/2/17/41; 40 tool rounds plus final nudge; retry attempts not counted")


if __name__ == "__main__":
    asyncio.run(main())
    check_full_solver_cap()
    check_full_solver_cap(stop_gate_at_cap=True)

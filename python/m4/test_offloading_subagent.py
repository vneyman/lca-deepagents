"""Offline checks for the data-retrieval and analysis handoff."""

import asyncio
import os
import runpy
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

from deepagents.backends import LocalShellBackend
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage

from tools import get_sp500_trading_data

LESSON = Path(__file__).with_name("m4.1_offloading_execute_skills_subagent.py")


class ScriptedModel(FakeMessagesListChatModel):
    offloading_notice: str = ""

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        result = super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
        if result.generations[0].message.content == "FORWARD_OFFLOADING_NOTICE":
            self.offloading_notice = messages[-1].text
            result.generations[0].message = AIMessage(content=self.offloading_notice)
        return result


def call(name, args, call_id):
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": call_id}])


class OffloadingSubagentTest(unittest.TestCase):
    def setUp(self):
        tracing = patch.dict(os.environ, {"LANGSMITH_TRACING": "false", "LANGCHAIN_TRACING_V2": "false"})
        tracing.start()
        self.addCleanup(tracing.stop)

    def test_parent_analyzes_complete_saved_data_for_large_and_small_results(self):
        for rows in (2, 10_000):
            with self.subTest(rows=rows), tempfile.TemporaryDirectory() as directory:
                csv_text = "ticker,date,close\n" + "TEST,2026-10-30,11\n" * rows
                path = "/large_tool_results/prices"
                responses = [
                    call("task", {"subagent_type": "data_researcher", "description": "Get prices"}, "research"),
                    call("get_sp500_trading_data", {"date_end": "2026-10-30", "trading_days": 2}, "prices"),
                ]
                responses.extend([
                    AIMessage(content="FORWARD_OFFLOADING_NOTICE"),
                    call("execute", {"command": (
                        f"{sys.executable} -c \"import pandas as pd; "
                        f"print('ROWS=' + str(len(pd.read_csv('{path.lstrip('/')}'))))\""
                    )}, "analyze"),
                    AIMessage(content="Analysis complete"),
                ])
                fake_models = ModuleType("models")
                fake_models.model = ScriptedModel(responses=responses)
                with (
                    patch.dict(sys.modules, {"models": fake_models}),
                    patch.object(sys, "path", [str(LESSON.parent), *sys.path]),
                ):
                    subagent = ModuleType("subagent.index_data_agent")
                    subagent.__dict__.update(runpy.run_path(str(LESSON.parent / "subagent/index_data_agent.py")))
                    with (
                        patch.dict(sys.modules, {"subagent.index_data_agent": subagent}),
                        patch("deepagents.backends.LocalShellBackend", side_effect=lambda **kwargs: LocalShellBackend(
                            root_dir=directory, virtual_mode=True,
                        )),
                    ):
                        lesson = runpy.run_path(str(LESSON))

                self.assertNotIn(get_sp500_trading_data, lesson["tools"])
                self.assertNotIn("OFFLOAD_THRESHOLD", {key for key in lesson if key.isupper()})
                with patch.object(get_sp500_trading_data, "func", return_value=csv_text):
                    result = asyncio.run(lesson["agent"].ainvoke(
                        {"messages": [{"role": "user", "content": "Analyze prices"}]},
                        config=lesson["THREAD"],
                    ))
                self.assertEqual((Path(directory) / path.lstrip("/")).read_text(), csv_text)
                handoff = next(message for message in result["messages"] if getattr(message, "tool_call_id", None) == "research")
                self.assertEqual(handoff.content, fake_models.model.offloading_notice.rstrip())
                self.assertIn(path, handoff.content)
                self.assertNotEqual(handoff.content, path)
                execution = next(message for message in result["messages"] if getattr(message, "tool_call_id", None) == "analyze")
                self.assertIn(f"ROWS={rows}", execution.content)
                self.assertEqual(result["messages"][-1].text, "Analysis complete")
                content = "Follow-up complete" if rows == 2 else [{"type": "text", "text": "Follow-up complete"}]
                fake_models.model.responses = [AIMessage(content=content)]
                fake_models.model.i = 0
                self.assertEqual(asyncio.run(lesson["turn"]("Summarize again")), "Follow-up complete")


if __name__ == "__main__":
    unittest.main()

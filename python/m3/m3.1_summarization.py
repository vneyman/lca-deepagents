"""
python/m3/m3.1_summarization.py

Demonstrates how the built-in SummarizationMiddleware compresses conversation
history when the context window fills up.

By default the trigger is 85% of the model's real context window (200k tokens
for Claude Haiku 4.5), which is impractical to hit in a demo. This example
overrides model.profile["max_input_tokens"] to a small value so summarization
fires after a few turns.

Run:
    cd python && uv run ./m3/m3.1_summarization.py
"""

import asyncio
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import StateBackend, FilesystemBackend
from deepagents.middleware import SummarizationMiddleware
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver

from models import model, strong_model

# Shrink the reported context window so summarization triggers at ~595 tokens
# (85% of 700) instead of the real threshold. Must use model object, not string.
# model.profile = {**model.profile, "max_input_tokens": 700}

print("*** MODEL INFO ***")
print(model)
print(model.profile)

# Directory where Deep Agents stores files
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
backend = FilesystemBackend(root_dir=DATA_DIR, virtual_mode=True)

agent = create_deep_agent(
    model=model,
    checkpointer=MemorySaver(),
    system_prompt="You are a helpful assistant. Keep every response to one sentence.",
    middleware=[
        SummarizationMiddleware(
            model=model, 
            trigger=("tokens", 20), 
            keep=("messages", 1),
            backend=backend
            )
        ]
)


THREAD = {"configurable": {"thread_id": "demo"}}

async def turn(message: str) -> str:
    result = await agent.ainvoke(
        {"messages": [HumanMessage(content=message)]},
        config=THREAD,
    )
    return result["messages"][-1].content[-1]["text"]  # type: ignore


async def show_state() -> None:
    state = await agent.aget_state(THREAD)
    messages = state.values.get("messages", [])
    event = state.values.get("_summarization_event")
    print(f"  stored : {len(messages)} message(s) (raw history, never trimmed)")
    if event:
        cutoff = event.get("cutoff_index", "?")
        print(f"  model saw : summary + messages[{cutoff}:]  [SUMMARIZED]")
        print(f"SUMMARY FILE: {event['file_path']}")
        print(f"SUMMARY: {event['summary_message'].content}")


async def main() -> None:
    turns = [
        "My name is Alex. I work at Acme Corp.",
        "What is 2 + 2?",
        "I have been building a distributed cache for three months.",
        "What is the capital of France?",
        "Describe in 3-5 sentense the cause of antisemitism",
        "What do you remember about me?",
    ]

    for i, message in enumerate(turns, 1):
        print(f"\n{'─' * 50}")
        print(f"Turn {i}  User:  {message}")
        response = await turn(message)
        print(f"Turn {i}  Agent: {response}")
        await show_state()


if __name__ == "__main__":
    asyncio.run(main())

# python/m2/m2.2_agent-test.py
import os
from pathlib import Path

from deepagents import FilesystemMiddleware, FilesystemPermission, create_deep_agent
from deepagents.backends import (
    CompositeBackend,
    FilesystemBackend,
    LocalShellBackend,
    StateBackend,
)
from langchain_core.tools import tool
from tavily import TavilyClient

from models import model

reference_dir = Path(__file__).parent / "reference"
reference_dir.mkdir(exist_ok=True)

# --- Tools -----------------------------------------------------------------
# internet_search belongs ONLY to the subagent (see `tools=` below).
tavily_api_key = os.environ.get("TAVILY_API_KEY")
if not tavily_api_key:
    raise RuntimeError(
        "TAVILY_API_KEY is required for the Module 2.2 test. "
    )

_tavily = TavilyClient(api_key=tavily_api_key)

backend = CompositeBackend(
    default=LocalShellBackend(
        root_dir=str(reference_dir),
        virtual_mode=True,
        inherit_env=True,
    ),
    routes={
        "/reference/": FilesystemBackend(
            root_dir=str(reference_dir),
            virtual_mode=True,
        ),
    },
)

@tool
def internet_search(query: str, max_results: int = 8) -> dict:
    """Search the web for recent news. Use this to research what's new in a
    music genre — new releases, notable artists, trends, and events."""
    return _tavily.search(query, max_results=max_results, topic="general")

SYSTEM_PROMPT = """
LOCAL PYTHON EXECUTION

You have access to a local shell through the execute tool.

The local Python environment is managed by uv.

When executing Python scripts:
1. Use `uv run`, never `python` or `python3`.
2. Execute scripts relative to the working directory.
3. For example: `uv run crime_rates_by_country.py`.
4. Execute every generated analysis script.
5. If execution fails, inspect the error, correct the script,
   and execute it again.
6. Never modify the source CSV file.
7. Do not report calculated results unless execution succeeded.
"""

agent = create_deep_agent(
    model=model,
    tools=[internet_search],
    system_prompt=SYSTEM_PROMPT,
    backend=backend,
)

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": (
                    "based on data in /reference/g10-crime-stats.csv, "
                    "create a python script to generate a table by country for antisimetic crime per capita, total crime rate per capita. "
                    "order by largest antisimetic crime rate. "
                    "If data is not available for a specific year, then skip that metric. "
                    "For example, if data is available for population is not available then skip that year, "
                    "and if data is available for population but not for antisimetic and total crime then add 'NA' for that metric. "
                    "Create and execute the Python script locally using `uv run <script>.py`. "
                    "Verify successful execution and report the calculated results. "
                ),
            }
        ]
    },
    config={"configurable": {"thread_id": "lab-m2.2-test"}},
)

# print(result["messages"][-1].content[0]["text"])
print(result["messages"][-1].content[-1]["text"])  # print the last message in the list

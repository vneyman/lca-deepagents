"""Delegate data retrieval and offloading; run skill-guided analysis in the parent.

The data_researcher returns Deep Agents' offloading notices with saved CSV paths.
The main agent loads the complete files with pandas via execute and reuses them
across turns.
"""

import asyncio
import sys
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, FilesystemBackend, LocalShellBackend
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from subagent.index_data_agent import build_data_researcher

from models import model, strong_model
from tools import internet_search

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

THREAD = {"configurable": {"thread_id": "test-offloading-skill-subagent"},
          "recursion_limit": 50}

tools = [internet_search]

backend = CompositeBackend(
    default=LocalShellBackend(root_dir=DATA_DIR, virtual_mode=True),
    routes={"/skills/": FilesystemBackend(root_dir=DATA_DIR.parent / "skills", virtual_mode=True)},
)

agent = create_deep_agent(
    name="Portfolio_Analyst",
    model=strong_model,
    tools=tools,
    skills=["/skills/"],
    checkpointer=MemorySaver(),
    system_prompt=(
        "You are a stock analyst of equities. Delegate historical data retrieval to "
        "data_researcher using the task tool, specifying the end date and number of trading sessions. "
        "The researcher returns Deep Agents' offloading notice through the task tool. "
        "Use the saved CSV path in that notice to load the complete data; its preview is incomplete. "
        "Perform all numerical analysis yourself using execute and the relevant skills. "
        # "Load /skills/summarize-portfolio/SKILL.md before ranking stocks or summarizing a portfolio. "
        "Use internet_search for company background and current news; results contain relevant passages in content. "
        "Load offloaded web search results as JSON to access content. "
        "For numerical analysis, generate and run Python code with pandas using the execute tool. "
        f"Use the Python interpreter {sys.executable!r}, which has pandas installed. "
        "Use pandas.read_csv to load the entire saved CSV returned by the researcher. "
        "Use only file paths actually returned by tools; do not assume a result was offloaded. "
        "For offloaded results, do not page through the dataset with read_file or calculate rankings from its preview. "
        "Shell commands run in the data directory. For Python file access, remove the leading '/' "
        "from virtual paths: '/large_tool_results/call_ID' becomes 'large_tool_results/call_ID'. "
        f"Skill scripts are on disk under {str(DATA_DIR.parent / 'skills')!r}; use that directory with execute. "
        "Process all rows, check missing data, and print only concise calculated results and row counts. "
        "For stock returns, state the price column and date endpoints used. "
        "Reuse saved data (including the offloaded files) for follow-up questions when appropriate. "
        "Report the saved data path and when you loaded it. "
        "Report if any skills were used to answer the question, and which skills were used. "
    ),
    backend=backend,
    subagents=[build_data_researcher(backend)],
)

async def turn(message: str) -> str:
    result = await agent.ainvoke(
        {"messages": [HumanMessage(content=message)]},
        config=THREAD,
    )
    return result["messages"][-1].text

async def main() -> None:
    turns = [
        """
        Today is November 9, 2026. 
        What are the top and bottom performing 5 stocks in the S&P 500 over the last 5 trading days? 
        """,
        "Include summary of the portfolio, assuming I hold $10,000 in the top and bottom 5 stocks (10 stock total) after day 1. ",
    ]

    for i, message in enumerate(turns, 1):
        print(f"Turn {i}: {message}")
        response = await turn(message)
        print(f"Response: {response}")

if __name__ == "__main__":
    asyncio.run(main())

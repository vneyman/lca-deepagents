import asyncio
import sys
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, FilesystemBackend, LocalShellBackend
from deepagents.middleware import FilesystemMiddleware
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver

from models import model
from tools import get_sp500_trading_data, internet_search

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

THREAD = {"configurable": {"thread_id": "test-offloading"}}
OFFLOAD_THRESHOLD = 20_000  # Offload after this many tokens

# ** TOOLS **
tools = [get_sp500_trading_data, internet_search]

backend = CompositeBackend(
    default=LocalShellBackend(root_dir=DATA_DIR, virtual_mode=True),
    routes={"/skills/": FilesystemBackend(root_dir=DATA_DIR.parent / "skills", virtual_mode=True)},
)

middleware = [
    FilesystemMiddleware(
        backend=backend,
        tool_token_limit_before_evict=OFFLOAD_THRESHOLD,
    )
]

agent = create_deep_agent(
    model=model,
    tools=tools,
    skills=["/skills/"],
    checkpointer=MemorySaver(),
    system_prompt=(
        "You are a stock analyst of equities with access to historical data via tools. "
        "Use internet_search for company background and current news; results contain relevant passages in content. "
        "Load offloaded web search results as JSON to access content. "
        "For numerical analysis, generate and run Python code with pandas using the execute tool. "
        f"Use the Python interpreter {sys.executable!r}, which has pandas installed. "
        "Tool results may contain complete inline CSV or a reference to an offloaded CSV file. "
        "For complete inline CSV, use pandas.read_csv(io.StringIO(csv_text)) with the exact returned CSV. "
        "When a tool result is offloaded, use pandas.read_csv to load the entire saved CSV. "
        "Use only file paths actually returned by tools; do not assume a result was offloaded. "
        "For offloaded results, do not page through the dataset with read_file or calculate rankings from its preview. "
        "Shell commands run in the data directory. For Python file access, remove the leading '/' "
        "from virtual paths: '/large_tool_results/call_ID' becomes 'large_tool_results/call_ID'. "
        "Process all rows, check missing data, and print only concise calculated results and row counts. "
        "For stock returns, state the price column and date endpoints used. "
        "Reuse saved data for follow-up questions when appropriate. "
        "Report whether the data was inline or offloaded. If offloaded, report its path and when you loaded it."
    ),
    middleware=middleware,
    backend=backend
)

async def turn(message: str) -> str:
    result = await agent.ainvoke(
        {"messages": [HumanMessage(content=message)]},
        config=THREAD,
    )
    return result["messages"][-1].content[-1]["text"]  # type: ignore

async def main() -> None:
    turns = [
        """
        Today is Friday, October 30, 2026. What are the top and bottom performing 5 stocks in the S&P 500 over the last 5 trading days?
        Trading day includes the current day, if not an exchange holiday. For example, 5 trading days from Friday, October 30, 2026 would be: October 30, October 29, October 28, October 27, and October 26.
        """,
        "When did those companies incorporate?"
    ]

    for i, message in enumerate(turns, 1):
        print(f"Turn {i}: {message}")
        response = await turn(message)
        print(f"Response: {response}")

if __name__ == "__main__":
    asyncio.run(main())

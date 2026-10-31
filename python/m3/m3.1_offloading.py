import asyncio
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend, StateBackend
from deepagents.middleware import FilesystemMiddleware, SummarizationMiddleware
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver

# from m5.homework import tools
from models import model, strong_model

from tools.get_sp500_trading_data import get_sp500_trading_data

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

THREAD = {"configurable": {"thread_id": "test-offloading"}}
OFFLOAD_THRESHOLD = 20_000  # Offload after this many tokens

# ** TOOLS **
tools = [
    get_sp500_trading_data
    ]

backend = FilesystemBackend(root_dir=DATA_DIR, virtual_mode=True)

middleware = [
    FilesystemMiddleware(
        backend=backend,
        tool_token_limit_before_evict=OFFLOAD_THRESHOLD,
    )
]

agent = create_deep_agent(
    model=model,
    tools=tools,
    checkpointer=MemorySaver(),
    system_prompt=(
        "You are a stock analyst of equities with access to historical data via tools."
        # "Use the get_sp500_trading_data tool to retrieve historical stock prices for S&P 500 companies."
        # "use the same data for multiple questions if possible."
        "Report where Deep Agent offloads data to disk and when it retrieves it back."
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
        Today is Friday, October 30, 2026. Using the get_sp500_trading_data tool, what are the top and bottom performing 5 stocks in the S&P 500 over the last 5 trading days?
        Trading day includes the current day, if not an exchange holiday. For example, 5 trading days from Friday, October 30, 2026 would be: October 30, October 29, October 28, October 27, and October 26.
        """,
        # "When did those companies incorporate?"
    ]

    for i, message in enumerate(turns, 1):
        print(f"Turn {i}: {message}")
        response = await turn(message)
        print(f"Response: {response}")

if __name__ == "__main__":
    asyncio.run(main())

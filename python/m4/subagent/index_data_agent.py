"""Retrieve S&P 500 data using Deep Agents' automatic tool-result offloading.

The parent supplies the shared backend. The researcher returns the middleware's
offloading notice so the main agent receives the saved file reference via task.
"""

from deepagents.backends.protocol import BackendProtocol
from deepagents.middleware import FilesystemMiddleware
from deepagents.middleware.subagents import SubAgent

from models import model, strong_model
from tools import get_sp500_trading_data

OFFLOAD_THRESHOLD = 1  # Every valid trading-data CSV exceeds this threshold.

DATA_RESEARCHER_PROMPT = """Retrieve S&P 500 trading data for the requested end date
and number of trading sessions using get_sp500_trading_data. Do not analyze it.

FilesystemMiddleware automatically offloads the CSV and provides a ToolMessage
containing the saved file path and a preview. Return that ToolMessage's text
unchanged as your final response so the main agent receives the framework's
offloading notice through the task tool. Do not extract only the path, summarize
the notice, or read and rewrite the saved data.

If retrieval or offloading fails, report the error instead of inventing a path.
"""


def build_data_researcher(backend: BackendProtocol) -> SubAgent:
    return {
        "name": "data_researcher",
        "model": model,
        "description": (
            "Retrieve S&P 500 historical trading data for a requested end date and "
            "number of trading sessions. Return Deep Agents' offloading notice "
            "unchanged, including the saved CSV path and preview, for the main agent to analyze."
        ),
        "system_prompt": DATA_RESEARCHER_PROMPT,
        "tools": [get_sp500_trading_data],
        "middleware": [FilesystemMiddleware(
            backend=backend,
            tool_token_limit_before_evict=OFFLOAD_THRESHOLD,
            tools=["read_file"],
        )],
    }

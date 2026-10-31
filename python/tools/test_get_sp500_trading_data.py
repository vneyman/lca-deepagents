import asyncio
import csv
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd
from deepagents.backends import FilesystemBackend
from deepagents.middleware import FilesystemMiddleware

from tools.get_sp500_trading_data import get_sp500_trading_data


class TradingDataOffloadingTest(unittest.TestCase):
    def test_offloaded_result_preserves_middle_rows_and_model_gets_path(self):
        companies = pd.DataFrame({
            "Symbol": ["TEST"],
            "Security": ["Test, Inc."],
            "GICS Sector": ["Industrials"],
        })
        prices = pd.DataFrame(
            {"Open": 10.0, "High": 12.0, "Low": 9.0,
             "Close": 11.0, "Adj Close": 11.0, "Volume": 100},
            index=pd.date_range(end="2026-10-30", periods=100, name="Date"),
        )
        with (
            patch("tools.get_sp500_trading_data.pd.read_csv", return_value=companies),
            patch("tools.get_sp500_trading_data.yf.download",
                  return_value=pd.concat({"TEST": prices}, axis=1)),
        ):
            message = get_sp500_trading_data.invoke({
                "type": "tool_call",
                "name": "get_sp500_trading_data",
                "id": "prices_test",
                "args": {"date_end": "2026-10-30", "trading_days": 100},
            })

        with tempfile.TemporaryDirectory() as directory:
            middleware = FilesystemMiddleware(
                backend=FilesystemBackend(root_dir=directory, virtual_mode=True),
                tool_token_limit_before_evict=100,
            )
            offloaded = asyncio.run(middleware._aintercept_large_tool_result(message))
            relative_path = "large_tool_results/prices_test"
            saved = (Path(directory) / relative_path).read_text()
            rows = list(csv.DictReader(io.StringIO(saved)))

        self.assertEqual(len(rows), 100)
        self.assertEqual(rows[50]["ticker"], "TEST")
        self.assertEqual(rows[50]["company"], "Test, Inc.")
        self.assertEqual(rows[50]["date"], "2026-09-11")
        self.assertEqual(rows[50]["close"], "11.0")
        self.assertEqual(saved, message.content)
        self.assertIn("/" + relative_path, offloaded.content)
        self.assertLess(len(offloaded.content), len(saved))


if __name__ == "__main__":
    unittest.main()

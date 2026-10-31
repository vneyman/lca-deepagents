import os
import runpy
import unittest
from pathlib import Path
from unittest.mock import patch

from pydantic import ValidationError

SCRIPT = Path(__file__).with_name("internet_search.py")


class InternetSearchTest(unittest.TestCase):
    def setUp(self):
        with patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"}):
            self.module = runpy.run_path(str(SCRIPT))
        self.search = self.module["internet_search"]

    def test_invalid_arguments_are_rejected_before_search(self):
        with patch.object(self.module["_tavily"], "search") as request:
            for args in (
                {"topic": "sports"},
                {"max_results": -1},
                {"max_results": 21},
            ):
                with self.subTest(args=args), self.assertRaises(ValidationError):
                    self.search.invoke({"query": "example", **args})
            request.assert_not_called()

    def test_defaults_topics_and_result_boundaries(self):
        response = {"results": []}
        with patch.object(self.module["_tavily"], "search", return_value=response) as request:
            self.assertEqual(self.search.invoke({"query": "example"}), response)
            request.assert_called_with(
                "example", max_results=3, topic="general", search_depth="advanced",
                chunks_per_source=2, include_raw_content=False,
            )
            for topic in ("general", "news", "finance"):
                for count in (0, 20):
                    with self.subTest(topic=topic, count=count):
                        self.assertEqual(self.search.invoke({
                            "query": "example", "topic": topic, "max_results": count,
                        }), response)
                        request.assert_called_with(
                            "example", max_results=count, topic=topic,
                            search_depth="advanced", chunks_per_source=2, include_raw_content=False,
                        )

    def test_relevant_passages_are_preserved(self):
        response = {"query": "example", "results": [{
            "title": "Example", "url": "https://example.com",
            "content": "First relevant passage. [...] Second relevant passage.",
            "raw_content": None, "score": 0.9,
        }]}
        with patch.object(self.module["_tavily"], "search", return_value=response):
            result = self.search.invoke({"query": "example"})
        self.assertEqual(result["results"][0]["content"],
                         "First relevant passage. [...] Second relevant passage.")

    def test_missing_key_explains_which_tool_requires_it(self):
        with patch.dict(os.environ, {"TAVILY_API_KEY": ""}):
            with self.assertRaisesRegex(RuntimeError, "TAVILY_API_KEY is required for internet search"):
                runpy.run_path(str(SCRIPT))


if __name__ == "__main__":
    unittest.main()

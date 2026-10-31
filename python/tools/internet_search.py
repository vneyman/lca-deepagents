import os
from typing import Annotated, Literal

from langchain_core.tools import tool
from pydantic import Field
from tavily import TavilyClient

tavily_api_key = os.environ.get("TAVILY_API_KEY")

if not tavily_api_key:
    raise RuntimeError(
        "TAVILY_API_KEY is required for internet search."
    )

_tavily = TavilyClient(api_key=tavily_api_key)


@tool
def internet_search(
    query: str,
    max_results: Annotated[int, Field(ge=0, le=20)] = 3,
    topic: Literal["general", "news", "finance"] = "general",
) -> dict:
    """Search the web with Tavily and retrieve relevant passages from each source.

    Use this tool to research facts, find news coverage, or locate financial
    information. Choose the topic based on the kind of sources needed.

    Args:
        query: A focused search question or keywords. Include relevant names,
            tickers, locations, or dates to make the request specific.
        max_results: Maximum number of sources to return, from 0 to 20.
            Defaults to 3. Use fewer for a quick lookup and more to compare
            sources. Zero returns no search results.
        topic: Search category; use exactly one of these values:
            - "general": Broad research, background facts, documentation,
              and explanations across varied sources. Default when unsure.
            - "news": Recent reporting and current events, such as political
              developments, sports updates, or company announcements.
            - "finance": Financial research about companies, stocks, markets,
              earnings, or the economy. Use "news" for breaking coverage
              and "general" for definitions of financial concepts.

    Returns:
        Tavily response dictionary containing the query and a results list.
        Each result includes a title, URL, relevance score, and content with
        up to two relevant chunks from the source. Each chunk targets about
        800 characters, roughly 1,600 characters per source. Full page content
        is not requested. Results may be empty or fewer than requested.

    Limitations:
        Chunk lengths are approximate, not a strict character or token limit.
        Passages may omit context from the full page. Advanced search uses
        more API credits than basic search.
        No explicit date filter is applied. Verify publication dates for
        time-sensitive questions. Financial results are web sources and do
        not guarantee live prices. API and network errors propagate to the caller.
    """

    return _tavily.search(
        query,
        max_results=max_results,
        topic=topic,
        search_depth="advanced",
        chunks_per_source=2,
        include_raw_content=False,
    )

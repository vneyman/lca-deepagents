import warnings
from datetime import date, timedelta

import pandas as pd

warnings.filterwarnings(
    "ignore",
    category=pd.errors.Pandas4Warning,
    module=r"yfinance\..*",
)

import yfinance as yf
from langchain_core.tools import tool


@tool
def get_sp500_trading_data(
    date_end: str = date.today().isoformat(),
    trading_days: int = 10,
) -> str:
    """
    Retrieve historical daily stock prices for all current S&P 500 constituents.

    Use this tool when analyzing S&P 500 stocks, comparing individual
    stock performance, examining trading activity, or retrieving market
    data for a specified historical period.

    The tool retrieves the current S&P 500 constituent list and downloads
    daily trading data from Yahoo Finance without requiring an API key.

    Args:
        date_end: Inclusive end date in YYYY-MM-DD format. If the date is
            not a trading day, use the most recent preceding trading day. Default is today.
        trading_days: Number of trading sessions to retrieve per stock,
            counting backward from date_end. Defaults to 10.

    Returns:
        Complete CSV text with one row per stock per trading session.
        Columns:
            ticker: Stock symbol.
            company: Company name.
            sector: GICS sector classification.
            date: Trading date.
            open: Opening price.
            high: Highest price.
            low: Lowest price.
            close: Closing price.
            adj_close: Dividend- and split-adjusted closing price.
            volume: Number of shares traded.

    Limitations:
        - Uses current S&P 500 membership, not historical membership.
        - Historical constituent analysis may have survivorship bias.
        - Missing market data may result in fewer rows for some stocks.
        - Yahoo Finance data is not guaranteed to be complete or accurate.
        - Today's data may represent an incomplete trading session.
    """

    if trading_days < 1:
        raise ValueError("trading_days must be positive")

    date_end = pd.Timestamp(date_end).date()

    # Download the constituent list.
    url = (
        "https://raw.githubusercontent.com/datasets/"
        "s-and-p-500-companies/main/data/constituents.csv"
    )

    companies = pd.read_csv(url)[
        ["Symbol", "Security", "GICS Sector"]
    ]
    companies.columns = ["ticker", "company", "sector"]

    # Yahoo Finance uses "-" instead of "." in ticker symbols.
    companies["yf_ticker"] = (
        companies["ticker"].str.replace(".", "-", regex=False)
    )

    # Allow extra calendar days for weekends and holidays.
    start = date_end - timedelta(days=max(30, trading_days * 3))
    end = date_end + timedelta(days=1)

    frames = []
    tickers = companies["yf_ticker"].tolist()

    # Download 50 tickers per batch.
    for i in range(0, len(tickers), 50):
        batch = tickers[i:i + 50]

        prices = yf.download(
            batch,
            start=start,
            end=end,
            group_by="ticker",
            auto_adjust=False,
            progress=False,
            threads=True,
        )

        for ticker in batch:
            if ticker not in prices.columns.get_level_values(0):
                continue

            data = (
                prices[ticker]
                .dropna(subset=["Close"])
                .tail(trading_days)
            )

            if not data.empty:
                frames.append(
                    data.assign(yf_ticker=ticker).reset_index()
                )

    if not frames:
        raise RuntimeError("No price data returned")

    result = pd.concat(frames, ignore_index=True)

    result = result.rename(columns={
        "Date": "date",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Adj Close": "adj_close",
        "Volume": "volume",
    })

    result = result.merge(companies, on="yf_ticker", how="left")
    result["date"] = pd.to_datetime(result["date"]).dt.date

    columns = [
        "ticker", "company", "sector", "date",
        "open", "high", "low", "close", "adj_close", "volume",
    ]

    return (
        result[columns]
        .sort_values(["ticker", "date"])
        .reset_index(drop=True)
        # A DataFrame is stringified as a truncated preview by LangChain.
        .to_csv(index=False)
    )

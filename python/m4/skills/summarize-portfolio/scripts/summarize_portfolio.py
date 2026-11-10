"""Summarize an in-memory price table using explicitly selected input columns."""

import pandas as pd


def summarize(
    data: pd.DataFrame,
    *,
    asset_column: str,
    date_column: str,
    price_column: str,
    name_column: str | None = None,
    equal_weight: bool = False,
) -> dict:
    required = {asset_column, date_column, price_column}
    if name_column is not None:
        required.add(name_column)
    if data.empty or not required.issubset(data.columns):
        raise ValueError(f"Expected nonempty table with selected columns: {sorted(required)}")
    if not pd.api.types.is_datetime64_any_dtype(data[date_column]):
        raise ValueError("Parse the selected date column using the source's verified date format first")
    source = data
    data = pd.DataFrame({
        "ticker": source[asset_column],
        "date": source[date_column],
        "price": source[price_column],
    })
    if name_column is not None:
        data["company"] = source[name_column]
    if data["ticker"].isna().any() or data["ticker"].astype(str).str.strip().eq("").any():
        raise ValueError("Every row must have a ticker")
    if data["date"].isna().any():
        raise ValueError("Every row must have a date")
    if data.duplicated(["ticker", "date"]).any():
        raise ValueError("Duplicate ticker/date rows; resolve them before summarizing")
    start, end = data["date"].min(), data["date"].max()
    if start == end:
        raise ValueError("At least two distinct trading dates are required")

    prices = pd.to_numeric(data["price"], errors="coerce")
    valid = prices.between(0, float("inf"), inclusive="neither")
    data["price"] = prices.where(valid)
    endpoints = data.pivot(index="ticker", columns="date", values="price")[[start, end]]
    eligible = endpoints.dropna()
    if eligible.empty:
        raise ValueError("No stocks have valid prices at both date endpoints")
    returns = ((eligible[end] / eligible[start] - 1) * 100).rename("return_pct")
    ranked = returns.reset_index()
    if "company" in data.columns:
        ranked = ranked.merge(data[["ticker", "company"]].drop_duplicates("ticker"), on="ticker")

    return {
        "date_start": start.date().isoformat(),
        "date_end": end.date().isoformat(),
        "trading_dates": int(data["date"].nunique()),
        "rows": len(data),
        "price_column": price_column,
        "portfolio_method": (
            "Equal-weight buy-and-hold across assets with both endpoints"
            if equal_weight else "Not calculated: portfolio weighting has not been specified"
        ),
        "portfolio_return_pct": float(returns.mean()) if equal_weight else None,
        "stocks_analyzed": len(returns),
        "excluded_tickers": endpoints.index.difference(eligible.index).tolist(),
        "missing_or_invalid_prices": int((~valid).sum()),
        "tickers_with_missing_dates": data.groupby("ticker")["date"].nunique().loc[
            lambda counts: counts < data["date"].nunique()
        ].index.tolist(),
        "top_performers": ranked.sort_values(
            ["return_pct", "ticker"], ascending=[False, True]
        ).head(5).to_dict(orient="records"),
        "bottom_performers": ranked.sort_values(
            ["return_pct", "ticker"], ascending=[True, True]
        ).head(5).to_dict(orient="records"),
    }

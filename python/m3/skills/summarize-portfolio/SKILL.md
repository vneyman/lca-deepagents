---
name: summarize-portfolio
description: Use when summarizing portfolio or stock-universe trading data, assessing overall performance, identifying top and bottom performers, or determining the date range covered by historical prices.
---

# Summarize Portfolio Trading Data

Inspect the supplied data before choosing how to load or analyze it. Do not
assume a file format, variable name, column name, date encoding, price basis,
portfolio weighting, or position history.

1. Identify the actual source and structure: an in-memory object, file, database,
   or tool response. Inspect its type, fields, metadata, and representative
   records. Use a reader appropriate to the observed format; JSON, spreadsheets,
   CSV, and in-memory data are all valid inputs. Analyze the complete dataset.
2. Establish which fields represent assets, observations, prices or valuations,
   holdings, and cash flows. Verify units, date formats, and financial meaning
   from the data or supplied documentation. Ask the user when these are ambiguous
   or required information is missing; do not infer meaning from names alone.
3. Determine the actual date range and observation count from the verified date
   field. Report coverage differences between assets and the requested period.
4. Use [scripts/summarize_portfolio.py](scripts/summarize_portfolio.py) for an
   asset-price table after loading it into a pandas DataFrame and parsing dates
   according to the verified source format. Import its `summarize` function and
   pass the data object plus explicit `asset_column`, `date_column`, and
   `price_column` arguments; pass `name_column` when identified. These arguments
   refer to the actual input fields. Resolve the helper relative to this skill's
   root. It requires pandas and does not read files or select input fields.
5. The helper calculates percentage price changes between common endpoints,
   returns top/bottom five assets, and reports missing data and exclusions.
   Use it only when that calculation fits the supplied data and request. For
   transaction records, portfolio valuations, or other structures, calculate
   performance with Python using the verified fields and an appropriate method.
6. Calculate overall portfolio performance from established holdings, weights,
   valuations, and cash flows. The helper leaves overall return unavailable by
   default. Pass `equal_weight=True` only when an equal-weight buy-and-hold
   calculation is explicitly appropriate. If portfolio performance cannot be
   established, state what information is missing rather than inventing weights.

Present the overall portfolio summary in its own section labeled
**PORTFOLIO SUMMARY**. Include actual date coverage, overall performance with
its calculation basis, and any data limitations or exclusions in that section.
Present ranked top and bottom performers in separate sections. State the price
or valuation basis and endpoints used. Adjust ranking counts to the request.
Distinguish a price-change calculation from realized portfolio returns.

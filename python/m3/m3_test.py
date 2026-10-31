from datetime import date
from io import StringIO

import pandas as pd

from tools.get_sp500_trading_data import get_sp500_trading_data

data_csv = get_sp500_trading_data.invoke(
    {
        "date_end": date.today().isoformat(),
        "trading_days": 2
    }
) # type: ignore
data_df = pd.read_csv(StringIO(data_csv))

print(get_sp500_trading_data.description)

print(data_df.head(10))
print(f"Tickers: {data_df['ticker'].nunique()}")
print(f"Rows: {len(data_df)}")

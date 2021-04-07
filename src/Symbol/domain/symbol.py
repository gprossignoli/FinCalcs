from dataclasses import dataclass

from pandas import DataFrame


@dataclass
class Symbol:
    ticker: str
    isin: str
    name: str
    historical_data: DataFrame

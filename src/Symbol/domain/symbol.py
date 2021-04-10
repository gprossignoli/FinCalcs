from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime

import pandas as pd
from pandas import DataFrame


@dataclass
class Symbol:
    ticker: str
    isin: str
    name: str
    historical_data: dict

    def __init__(self, ticker: str, isin: str, name: str, historical_data: dict):
        self.ticker = ticker
        self.isin = isin
        self.name = name
        self.historical_data = self.__process_historical_data(historical_data)

    @staticmethod
    def __process_historical_data(data: dict) -> dict[str, pd.Series]:
        indexes = tuple(datetime.strptime(i, '%Y-%m-%d %H:%M:%S').date() for i in tuple(data['close'].keys()))
        closures = pd.Series(data=data['close'].values(), index=indexes)
        dividends = pd.Series(data=data['dividends'].values(), index=indexes)
        return {'closures': closures, 'dividends': dividends}

    @property
    def first_date(self):
        return self.historical_data.get('closures').index[0]

    @property
    def last_date(self):
        return self.historical_data.get('closures').index[-1]

    @property
    def daily_returns(self) -> pd.Series:
        if self.historical_data.get('returns') is not None:
            return self.historical_data.get('returns')
        normalized_returns = self.historical_data['closures'] / self.historical_data['closures'].iloc[0]
        self.historical_data['returns'] = normalized_returns
        return normalized_returns


SymbolInformation = namedtuple("SymbolInformation", "ticker, isin, name, closures, dividends, returns")

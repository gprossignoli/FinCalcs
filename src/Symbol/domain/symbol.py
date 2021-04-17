from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime

import pandas as pd


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
        self.historical_data = self._process_historical_data(historical_data)
        self.closures = self.historical_data['closures']

    @staticmethod
    def _process_historical_data(data: dict) -> dict[str, pd.Series]:
        try:
            indexes = tuple(datetime.strptime(i, '%Y-%m-%d %H:%M:%S').date() for i in tuple(data['close'].keys()))
        except ValueError:
            indexes = tuple(datetime.strptime(i, '%Y-%m-%d').date() for i in tuple(data['close'].keys()))

        closures = pd.Series(data=data['close'].values(), index=indexes)
        closures.index = pd.to_datetime(closures.index)
        dividends = pd.Series(data=data['dividends'].values(), index=indexes)
        dividends.index = pd.to_datetime(dividends.index)
        if data.get('daily_returns') is not None:
            daily_returns = pd.Series(data=data['daily_returns'].values(), index=indexes)
            daily_returns.index = pd.to_datetime(daily_returns.index)
            return {'closures': closures, 'dividends': dividends, 'daily_returns': daily_returns}

        return {'closures': closures, 'dividends': dividends}

    @property
    def first_date(self):
        return self.historical_data.get('closures').index[0]

    @property
    def last_date(self):
        return self.historical_data.get('closures').index[-1]

    @property
    def daily_returns(self) -> pd.Series:
        if self.historical_data.get('daily_returns') is not None:
            return self.historical_data.get('daily_returns')
        self.historical_data['daily_returns'] = self.historical_data['closures'].pct_change()
        return self.historical_data['daily_returns']

    def cagr(self, period: str):
        """
        Compound annual growth rate
        :param period: could be '3yr' or '5yr'
        :return:
        """
        today = self.closures.index[-1]
        today = datetime(today.year, today.month, today.day)
        if period == '3yr':
            n = 3
            first_date = datetime(today.year - 3, today.month, today.day)
        elif period == '5yr':
            n = 5
            first_date = datetime(today.year - 5, today.month, today.day)

        closes = self.closures[self.closures.index >= first_date]
        cagr = (closes[-1] / closes[0])**1/n - 1
        return cagr

    def add_new_day(self, close_price: float, date: datetime, dividend: float):
        self.historical_data['closures'] = self.historical_data['closures'].append(pd.Series(index=[date],
                                                                                             data=[close_price]))
        self.historical_data['daily_returns'] = self.historical_data['closures'].pct_change()
        self.historical_data['dividends'] = self.historical_data['dividends'].append(pd.Series(index=[date],
                                                                                               data=[dividend]))


class Index(Symbol):
    @staticmethod
    def _process_historical_data(data: dict) -> dict[str, pd.Series]:
        try:
            indexes = tuple(datetime.strptime(i, '%Y-%m-%d %H:%M:%S').date() for i in tuple(data['close'].keys()))
        except ValueError:
            indexes = tuple(datetime.strptime(i, '%Y-%m-%d').date() for i in tuple(data['close'].keys()))

        closures = pd.Series(data=data['close'].values(), index=indexes)
        closures.index = pd.to_datetime(closures.index)
        if data.get('daily_returns') is not None:
            daily_returns = pd.Series(data=data['daily_returns'].values(), index=indexes)
            daily_returns.index = pd.to_datetime(daily_returns.index)
            return {'closures': closures, 'daily_returns': daily_returns}

        return {'closures': closures}


SymbolInformation = namedtuple("SymbolInformation", "ticker, isin, name, closures, dividends, daily_returns")

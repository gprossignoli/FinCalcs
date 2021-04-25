from datetime import datetime
from typing import Union, Any

import pandas as pd


class Symbol:
    def __init__(self, ticker: str, name: str, closures: dict, daily_returns: dict = None):
        self.ticker = ticker
        self.name = name
        self.closures, processed_daily_returns = self._process_historical_data(closures, daily_returns)
        self.daily_returns = (self._compute_daily_returns()
                              if processed_daily_returns is None else processed_daily_returns)

    @staticmethod
    def _process_historical_data(closures: dict, daily_returns: dict = None) -> tuple[pd.Series,
                                                                                      Union[pd.Series, None]]:
        """
        :param closures: closures of the symbol as dict
        :param daily_returns: (optional) daily_returns of the symbol as dict, if None, would be computed.
        :return: historic data of the symbol with properly pd.Series
        """
        try:
            indexes = tuple(datetime.strptime(i, '%Y-%m-%d %H:%M:%S').date() for i in tuple(closures.keys()))
        except ValueError:
            indexes = tuple(datetime.strptime(i, '%Y-%m-%d').date() for i in tuple(closures.keys()))

        pd_closures = pd.Series(data=closures.values(), index=indexes)
        pd_closures.index = pd.to_datetime(pd_closures.index)
        if daily_returns is not None:
            pd_daily_returns = pd.Series(data=daily_returns.values(), index=indexes)
            pd_daily_returns.index = pd.to_datetime(pd_daily_returns.index)
            return pd_closures, pd_daily_returns

        return pd_closures, None

    @property
    def first_date(self):
        return self.closures.index[0]

    @property
    def last_date(self):
        return self.closures.index[-1]

    def _compute_daily_returns(self) -> pd.Series:
        self.daily_returns = self.closures.pct_change()
        return self.daily_returns


class Index(Symbol):
    pass


class Stock(Symbol):
    def __init__(self, ticker: str, isin: str, name: str, closures: dict, dividends: dict,
                 exchange: str, daily_returns: dict = None):
        super(Stock, self).__init__(ticker=ticker, name=name, closures=closures, daily_returns=daily_returns)
        self.dividends = self._process_dividends_data(dividends)
        self.isin = isin
        self.exchange = exchange

    def _process_dividends_data(self, dividends: dict) -> pd.Series:
        """
        :param dividends: dict
        :return: historic data of the symbol with properly pd.Series
        """
        pd_dividends = pd.Series(data=dividends.values(), index=self.closures.index)
        return pd_dividends

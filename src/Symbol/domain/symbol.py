from datetime import datetime
from typing import Union

import pandas as pd


class Symbol:
    def __init__(self, ticker: str, isin: str, name: str, closures: dict, daily_returns: dict = None):
        self.ticker = ticker
        self.isin = isin
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
        if self.daily_returns is not None:
            return self.daily_returns
        self.daily_returns = self.closures.pct_change()
        return self.daily_returns


class Index(Symbol):
    pass


class Stock(Symbol):
    def __init__(self, ticker: str, isin: str, name: str, closures: dict, dividends: dict,
                 daily_returns: dict = None):
        super().__init__(ticker=ticker, isin=isin, name=name, closures=closures, daily_returns=daily_returns)

        self.closures, self.dividends, processed_daily_returns = \
            self._process_historical_data(closures=closures, daily_returns=daily_returns, dividends=dividends)

        self.daily_returns = (self._compute_daily_returns()
                              if processed_daily_returns is None else processed_daily_returns)

    def _process_historical_data(self, closures: dict,
                                 daily_returns: dict = None, **kwargs) -> tuple[pd.Series, pd.Series,
                                                                                Union[pd.Series, None]]:
        """
        :param closures: closures of the symbol as dict
        :param daily_returns: (optional) daily_returns of the symbol as dict, if None, would be computed.
        :param args: only expected dividends: dict (same as closures but for dividends)
        :return: historic data of the symbol with properly pd.Series
        """
        dividends = kwargs['dividends']

        pd_closures, pd_daily_returns = super(Stock, self)._process_historical_data(closures, daily_returns)

        pd_dividends = pd.Series(data=dividends.values(), index=pd_closures.index)
        if pd_daily_returns is not None:
            return pd_closures, pd_dividends, pd_daily_returns

        return pd_closures, pd_dividends, None

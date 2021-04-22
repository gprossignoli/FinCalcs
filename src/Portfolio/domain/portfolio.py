import math

import numpy as np
import pandas as pd
from pandas import DataFrame

from src.Symbol.domain.symbol import Symbol
from src import settings as st


class Portfolio:
    def __init__(self, symbols: tuple[Symbol], n_shares_per_symbol: dict[str, int]):
        self.symbols = symbols
        self.total_shares = sum(n_shares_per_symbol.values())
        self.weights = {symbol.ticker: (n_shares_per_symbol[symbol.ticker] / self.total_shares)
                        for symbol in symbols}
        self.first_date, self.last_date = self.__compute_common_date()

    @property
    def weighted_returns(self) -> pd.Series:
        weighted_rets = DataFrame(data=[symbol.daily_returns[self.first_date:self.last_date]
                                  .rename(index=symbol.ticker, inplace=True) * self.weights[symbol.ticker]
                                        for symbol in self.symbols]).transpose()
        return weighted_rets.sum(axis=1)

    @property
    def volatility(self):
        return self.weighted_returns.std()

    @property
    def annualized_volatility(self):
        return self.volatility * math.sqrt(st.ANNUALIZATION_FACTOR)

    @property
    def annualized_returns(self):
        start_date = self.weighted_returns.index[0]
        end_date = self.weighted_returns.index[-1]
        months_passed = (end_date - start_date) / np.timedelta64(1, "M")

        total_return = (self.weighted_returns[-1] - self.weighted_returns[1]) / self.weighted_returns[1]
        total_return_arr = np.array([1+total_return])

        return (np.float_power(abs(total_return_arr),
                               np.array([12/months_passed]))*np.sign(total_return_arr)) - 1

    @property
    def mdd(self):
        """
        Max Drawdown
        """
        cum_rets = self.weighted_returns.add(1).cumprod()
        nav = ((1 + cum_rets) * 100).fillna(100)
        hwm = nav.cummax()
        dd = nav / hwm - 1
        return min(dd)

    def __compute_common_date(self) -> tuple:
        common_idx = self.symbols[0].daily_returns.index
        for symbol in self.symbols:
            common_idx = common_idx.intersection(symbol.daily_returns.index)
        return common_idx[0], common_idx[-1]

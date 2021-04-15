import math

import pandas as pd
from pandas import DataFrame

from src.Symbol.domain.symbol import Symbol
from src import settings as st


class Portfolio:
    def __init__(self, symbols: tuple[Symbol], n_stocks_per_symbol: dict[str, int]):
        self.symbols = symbols
        self.total_stocks = sum(n_stocks_per_symbol.values())
        self.weights = {symbol.ticker: (n_stocks_per_symbol[symbol.ticker]/self.total_stocks)
                        for symbol in symbols}
        self.first_date, self.last_date = self.__compute_common_date()

    @property
    def weighted_returns(self) -> pd.Series:
        weighted_rets = DataFrame(data=[symbol.historical_data['daily_returns'][self.first_date:self.last_date]
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
        cumulative_return = (self.weighted_returns[-1] - self.weighted_returns[1])\
                            / self.weighted_returns[1]
        return (1 + cumulative_return)**(365/st.ANNUALIZATION_FACTOR) - 1

    def sharpe_ratio(self):
        return (self.annualized_returns - st.RISK_FREE_RATIO) / self.annualized_volatility

    def sortino_ratio(self, benchmark_returns: pd.Series):
        neg_asset_returns = (self.weighted_returns[self.weighted_returns < 0][self.first_date:self.last_date])
        std_dev = neg_asset_returns.std()
        return (self.annualized_returns - benchmark_returns) / (std_dev * math.sqrt(st.ANNUALIZATION_FACTOR))

    def __compute_common_date(self) -> tuple:
        common_idx = self.symbols[0].daily_returns.index
        for symbol in self.symbols:
            common_idx = common_idx.intersection(symbol.historical_data['daily_returns'].index)
        return common_idx[0], common_idx[-1]

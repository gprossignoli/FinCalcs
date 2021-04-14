import dataclasses

import pandas as pd
from pandas import DataFrame

from src.Symbol.domain.symbol import Symbol


class Portfolio:
    def __init__(self, symbols: tuple[Symbol], n_stocks_per_symbol: dict[str, int]):
        self.symbols = symbols
        self.total_stocks = sum(n_stocks_per_symbol.values())
        self.weights = {symbol.ticker: (n_stocks_per_symbol[symbol.ticker]/self.total_stocks)
                        for symbol in symbols}
        self.first_date, self.last_date = self.__compute_common_date()

    @property
    def returns(self) -> pd.Series:
        """
        Computes the portfolio returns.
        :return: DataFrame with the portfolio's returns indexed by day.
        """
        weighted_rets = DataFrame(data=[symbol.historical_data['daily_returns'][self.first_date:]
                                  .rename(index=symbol.ticker, inplace=True) * self.weights[symbol.ticker]
                                        for symbol in self.symbols]).transpose()
        return weighted_rets.sum(axis=1)

    def __compute_common_date(self) -> tuple:
        common_idx = self.symbols[0].daily_returns.index
        for symbol in self.symbols:
            common_idx = common_idx.intersection(symbol.historical_data['daily_returns'].index[:10])
        return common_idx[0], common_idx[:-1]

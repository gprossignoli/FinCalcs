import datetime
from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.Portfolio.domain.portfolio import Portfolio
from src.Symbol.domain.symbol import Symbol
from src import settings as st


@dataclass
class PortfolioTransfer:
    symbols: tuple[str]
    total_shares: int
    weights: dict[str, float]
    first_date: datetime.date
    last_date: datetime.date
    returns: dict[str, str]
    volatility: dict[str, str]

    def to_json(self):
        return {
            'symbols': self.symbols,
            'total_shares': self.total_shares,
            'weights': {k: str(v) for k, v in self.weights.items()},
            'first_date': self.first_date.strftime("%d-%m-%Y"),
            'last_date': self.last_date.strftime("%d-%m-%Y"),
            'returns': self.returns,
            'volatility': self.volatility
        }


@dataclass
class PortfolioStatisticsTransfer(PortfolioTransfer):
    annualized_returns: float
    annualized_volatility: float
    maximum_drawdown: float
    sharpe_ratio: float
    sortino_ratio: dict[str, float]
    calmar_ratio: float

    def to_json(self):
        json = super().to_json()
        json['annualized_returns'] = str(self.annualized_returns)
        json['annualized_volatility'] = str(self.annualized_volatility)
        json['maximum_drawdown'] = str(self.maximum_drawdown)
        json['sharpe_ratio'] = str(self.sharpe_ratio)
        json['sortino_ratio'] = {k: str(v) for k, v in self.sortino_ratio.items()}
        json['calmar_ratio'] = str(self.calmar_ratio)
        return json


class DomainService:
    @staticmethod
    def create_portfolio_entity(symbols: tuple[Symbol], n_shares_per_symbols: dict[str, int]) -> Portfolio:
        return Portfolio(symbols=symbols, n_shares_per_symbol=n_shares_per_symbols)

    @staticmethod
    def sharpe_ratio(entity: Portfolio):
        return float(((entity.annualized_returns - st.RISK_FREE_RATIO) / entity.annualized_volatility)[0])

    @staticmethod
    def sortino_ratio(entity: Portfolio, benchmark_returns: pd.Series):
        neg_asset_returns = (entity.weighted_returns[entity.weighted_returns < 0][entity.first_date:entity.last_date])
        std_dev = neg_asset_returns.std()
        return float(((entity.annualized_returns - benchmark_returns.mean())
                      / (std_dev * np.sqrt(st.ANNUALIZATION_FACTOR)))[0])

    @staticmethod
    def calmar_ratio(entity: Portfolio):
        return float(((entity.annualized_returns - st.RISK_FREE_RATIO) / entity.mdd)[0])

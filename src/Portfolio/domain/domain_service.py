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
    returns: dict
    volatility: dict

    def to_json(self):
        return {
            'symbols': self.symbols,
            'total_shares': self.total_shares,
            'weights': {k: str(v) for k, v in self.weights.items()},
            'first_date': self.first_date.strftime("%d-%m-%Y"),
            'last_date': self.last_date.strftime("%d-%m-%Y"),
            'returns': {k.strftime('%d-%m-%Y'): str(round(v, 4)).replace('nan', 'null')
                        for k, v in self.returns.items()},
            'volatility': {k.strftime('%d-%m-%Y'): str(round(v, 4)).replace('nan', 'null')
                           for k, v in self.volatility.items()}
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
        json['annualized_returns'] = str(round(self.annualized_returns, 4))
        json['annualized_volatility'] = str(round(self.annualized_volatility, 4))
        json['maximum_drawdown'] = str(round(self.maximum_drawdown, 4))
        json['sharpe_ratio'] = str(round(self.sharpe_ratio, 4))
        json['sortino_ratio'] = {k: str(round(v, 4)) for k, v in self.sortino_ratio.items()}
        json['calmar_ratio'] = str(round(self.calmar_ratio, 4))
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

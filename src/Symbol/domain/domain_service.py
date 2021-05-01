import typing
from dataclasses import dataclass
from datetime import datetime
from typing import Union, Literal

from src.Symbol.domain.symbol import Symbol, Index, Stock
from src import settings as st


@dataclass
class SymbolTransfer:
    """
    first_date: Year%month%day%
    last_date: Year%month%day%
    closures: {Year%month%day%: float}
    daily_returns: {Year%month%day%: float}
    """
    ticker: str
    name: str
    first_date: datetime.timestamp
    last_date: datetime.timestamp
    closures: dict
    daily_returns: dict

    def to_json(self):
        json = {'ticker': self.ticker, 'name': self.name,
                'first_date': self.first_date.strftime('%d-%m-%Y'), 'last_date': self.last_date.strftime('%d-%m-%Y'),
                'closures': {k.strftime('%d-%m-%Y'): str(round(v, 4)).replace('nan', 'null')
                             for k, v in self.closures.items()},
                'daily_returns': {k.strftime('%d-%m-%Y'): str(round(v, 4)).replace('nan', 'null')
                                  for k, v in self.daily_returns.items()}}
        return json


@dataclass
class SymbolStatisticsTransfer(SymbolTransfer):
    """
    cagr: {"3yr": float, "5yr": float}
    """
    cagr: dict

    def to_json(self):
        json = super(SymbolStatisticsTransfer, self).to_json()
        json['cagr'] = {k: str(round(v, 4)) for k, v in self.cagr.items()}
        return json


@dataclass
class StockTransfer(SymbolStatisticsTransfer):
    """
    dividends: {Year%month%day%: float}
    """
    dividends: dict
    exchange: str
    isin: str

    def to_json(self):
        json = super(StockTransfer, self).to_json()
        json['dividends'] = {k.strftime('%d-%m-%Y'): str(round(v, 4)).replace('nan', 'null')
                             for k, v in self.dividends.items()}
        json['isin'] = self.isin
        json['exchange'] = self.exchange
        return json


@dataclass
class IndexTransfer(SymbolStatisticsTransfer):
    pass


@dataclass
class SymbolInformationTransfer:
    ticker: str
    name: str
    last_price: dict
    last_return: dict

    def to_json(self):
        json = {'ticker': self.ticker, 'name': self.name,
                'last_price': {k: str(v) for k, v in self.last_price.items()},
                'last_return': {k: str(v) for k, v in self.last_return.items()}}
        return json


@dataclass
class StockInformationTransfer(SymbolInformationTransfer):
    exchange: str
    isin: str

    def to_json(self):
        json = super(StockInformationTransfer, self).to_json()
        json['exchange'] = self.exchange
        json['isin'] = self.isin
        return json


class DomainService:
    @staticmethod
    def create_symbol_entity(ticker: str, closures: dict, name: str,
                             isin: str = None, exchange: str = None,
                             dividends: dict = None, daily_returns: dict = None) -> Symbol:
        if dividends is not None and exchange is not None:
            return Stock(ticker=ticker, isin=isin, name=name, closures=closures,
                         dividends=dividends, daily_returns=daily_returns, exchange=exchange)
        elif ticker in st.EXCHANGES:
            return Index(ticker=ticker, name=name, closures=closures, daily_returns=daily_returns)

        else:
            return Symbol(ticker=ticker, name=name, closures=closures, daily_returns=daily_returns)

    @staticmethod
    def compute_cagr(entity: Union[Index, Stock], period: Literal['3yr', '5yr'] = '3yr') -> float:
        """
        Compound annual growth rate
        :param entity: Entity for which compute the cagr.
        :param period: could be '3yr' or '5yr'
        """
        if period not in ["3yr", "5yr"]:
            raise AttributeError

        today = entity.closures.index[-1]
        today = datetime(today.year, today.month, today.day)
        if period == '3yr':
            n = 3
            first_date = datetime(today.year - 3, today.month, today.day)
        elif period == '5yr':
            n = 5
            first_date = datetime(today.year - 5, today.month, today.day)

        closes = entity.closures[entity.closures.index >= first_date]
        cagr = ((closes[-1] / closes[0]) ** (1 / n)) - 1
        return cagr

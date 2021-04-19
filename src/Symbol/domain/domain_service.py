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
    isin: str
    name: str
    first_date: str
    last_date: str
    closures: dict
    daily_returns: dict


@dataclass
class SymbolStatisticsTransfer(SymbolTransfer):
    """
    cagr: {"3yr": float, "5yr": float}
    """
    cagr: dict


@dataclass
class StockTransfer(SymbolStatisticsTransfer):
    """
    dividends: {Year%month%day%: float}
    """
    dividends: dict


@dataclass
class IndexTransfer(SymbolStatisticsTransfer):
    pass


@dataclass
class SymbolInformationTransfer:
    ticker: str
    isin: str
    name: str


class DomainService:
    @staticmethod
    def create_symbol_entity(ticker: str, isin: str, name: str,
                             closures: dict, exchange: str = None,
                             dividends: dict = None, daily_returns: dict = None) -> Symbol:
        if dividends is not None and exchange is not None:
            return Stock(ticker=ticker, isin=isin, name=name, closures=closures,
                         dividends=dividends, daily_returns=daily_returns, exchange=exchange)
        elif ticker in st.EXCHANGES:
            return Index(ticker=ticker, isin=isin, name=name, closures=closures, daily_returns=daily_returns)

        else:
            return Symbol(ticker=ticker, isin=isin, name=name, closures=closures, daily_returns=daily_returns)

    def compute_cagr(self, entity: Union[Index, Stock], period: Literal['3yr', '5yr'] = '3yr') -> float:
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
        cagr = (closes[-1] / closes[0]) ** 1 / n - 1
        return cagr

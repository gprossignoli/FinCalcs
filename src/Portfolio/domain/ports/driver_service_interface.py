from abc import ABCMeta, abstractmethod
from datetime import datetime

from src.Portfolio.domain.domain_service import DomainService, PortfolioStatisticsTransfer
from src.Portfolio.domain.portfolio import Portfolio
from src.Symbol.domain.ports.repository_interface import RepositoryInterface as SymbolRepositoryInterface
from src.Symbol.domain.domain_service import DomainService as SymbolDomainService


class DriverServiceInterface(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'create_portfolio') and
                callable(subclass.create_portfolio) and
                hasattr(subclass, '_compute_portfolio_statistics') and
                callable(subclass._compute_portfolio_statistics)) or NotImplemented

    def __init__(self, symbol_repository: SymbolRepositoryInterface, domain_service: DomainService,
                 symbol_domain_service: SymbolDomainService):
        self.symbol_repository = symbol_repository
        self.symbol_domain_service = symbol_domain_service
        self.domain_service = domain_service

    @abstractmethod
    def create_portfolio(self, tickers: tuple[str], n_shares_per_symbol: dict[str, int],
                         initial_date: datetime.date, end_date: datetime.date) -> PortfolioStatisticsTransfer:
        raise NotImplemented

    @abstractmethod
    def _compute_portfolio_statistics(self, entity: Portfolio):
        raise NotImplemented

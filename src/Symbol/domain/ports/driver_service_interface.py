from abc import ABCMeta, abstractmethod
from typing import Union

from src.Symbol.domain.ports.repository_interface import RepositoryInterface
from src.Symbol.domain.domain_service import DomainService, SymbolInformationTransfer, SymbolStatisticsTransfer


class DriverServiceInterface(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'get_symbol') and
                callable(subclass.get_symbol) and
                hasattr(subclass, 'get_stocks_info') and
                callable(subclass.get_stocks_info) and
                hasattr(subclass, 'get_indexes_info') and
                callable(subclass.get_indexes_info)) or NotImplemented

    def __init__(self, repository: RepositoryInterface, domain_service: DomainService):
        self.repository = repository
        self.domain_service = domain_service

    @abstractmethod
    def get_stocks_info(self) -> tuple[SymbolInformationTransfer, ...]:
        """
        Looks for the stocks info.

        :return: Each stock info or an empty tuple if stock not found.
        """
        raise NotImplemented

    @abstractmethod
    def get_indexes_info(self) -> tuple[SymbolInformationTransfer, ...]:
        """
        Looks for the indexes info.

        :return: Each index info or an empty tuple if stock not found.
        """
        raise NotImplemented

    @abstractmethod
    def get_symbol(self, symbol_ticker: str) -> Union[SymbolStatisticsTransfer, bool]:
        """
        Looks for the symbol using the ticker provided, and returns its info and statistics.

        :param symbol_ticker: ticker of the symbol.
        :return: symbol's info and statistics or False if symbol not found.
        """
        raise NotImplemented

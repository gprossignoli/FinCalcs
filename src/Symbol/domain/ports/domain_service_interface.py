import typing
from abc import ABCMeta, abstractmethod

from pandas import DataFrame

from src.Symbol.domain.ports.repository_interface import RepositoryInterface
from src.Symbol.domain.symbol import Symbol


class DomainServiceInterface(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'fetch_symbol_data') and
                callable(subclass.fetch_symbol_data) and
                hasattr(subclass, 'create_symbol_entity') and
                callable(subclass.create_symbol_entity)) or NotImplemented

    def __init__(self, repository: RepositoryInterface = None):
        self.repository = repository

    @abstractmethod
    def fetch_symbol_data(self) -> None:
        """
        Gets the symbol data, converts it to a symbol entity,
        precalculates it's financials data, and saves into the db.
        :param symbol_data:  dictionary with all the information.
        """
        raise NotImplemented

    @abstractmethod
    def create_symbol_entity(self, ticker: str, isin: str, name: str, historic_data: DataFrame) -> Symbol:
        raise NotImplemented

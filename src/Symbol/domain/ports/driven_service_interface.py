from abc import ABCMeta, abstractmethod

from src.Symbol.domain.ports.repository_interface import RepositoryInterface
from src.Symbol.domain.domain_service import DomainService


class DrivenServiceInterface(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'fetch_symbol_data') and
                callable(subclass.fetch_symbol_data) and
                hasattr(subclass, 'save_stock') and
                callable(subclass.save_stock) and
                hasattr(subclass, 'save_index') and
                callable(subclass.save_index)) or NotImplemented

    def __init__(self, repository: RepositoryInterface, domain_service: DomainService):
        self.repository = repository
        self.domain_service = domain_service

    @abstractmethod
    def fetch_symbol_data(self) -> None:
        """
        Gets the symbol data, converts it to a symbol entity,
        precalculates it's financials data, and saves into the db.
        """
        raise NotImplemented

    @abstractmethod
    def save_stock(self, stock_info: dict) -> None:
        """
        Saves a symbol of type stock.
        """
        raise NotImplemented

    @abstractmethod
    def save_index(self, index_info: dict) -> None:
        """
        Saves a symbol of type index.
        """
        raise NotImplemented

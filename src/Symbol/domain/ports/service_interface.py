from abc import ABCMeta, abstractmethod

from pandas import DataFrame

from src.Symbol.domain.ports.repository_interface import RepositoryInterface
from src.Symbol.domain.symbol import Symbol, Index


class ServiceInterface(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'create_symbol_entity') and
                callable(subclass.create_symbol_entity) and
                hasattr(subclass, 'create_index_entity') and
                callable(subclass.create_index_entity)
                ) or NotImplemented

    def __init__(self, repository: RepositoryInterface = None):
        self.repository = repository

    @abstractmethod
    def create_symbol_entity(self, *args) -> Symbol:
        raise NotImplemented

    @abstractmethod
    def create_index_entity(self, *args) -> Index:
        raise NotImplemented

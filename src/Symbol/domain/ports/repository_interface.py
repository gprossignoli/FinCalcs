from abc import ABCMeta, abstractmethod
from typing import Union, Literal

from src.Symbol.domain.symbol import Stock, Index


class RepositoryInterface(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'save_stock') and
                callable(subclass.save_stock) and
                hasattr(subclass, 'save_index') and
                callable(subclass.save_index) and
                hasattr(subclass, 'get_symbol') and
                callable(subclass.get_symbol) and
                hasattr(subclass, 'get_symbols') and
                callable(subclass.get_symbols) and
                hasattr(subclass, 'get_all_symbols') and
                callable(subclass.get_all_symbols) and
                hasattr(subclass, 'clean_old_symbols') and
                callable(subclass.clean_old_symbols)
                ) or NotImplemented

    @abstractmethod
    def save_stock(self, stock: Stock) -> None:
        """
        Save a stock entity into the db
        """
        raise NotImplemented

    @abstractmethod
    def save_index(self, index: Index) -> None:
        """
        Save a index entity into the db
        """
        raise NotImplemented

    @abstractmethod
    def get_symbol(self, ticker: str) -> Union[dict, bool]:
        """
        Gets the symbol from the db.
        :param ticker: ticker of the symbol
        :return: Symbol information or False if none were found.
        """
        raise NotImplemented

    @abstractmethod
    def get_symbols(self, tickers: tuple[str, ...]) -> Union[tuple[dict, ...], bool]:
        """
        Gets the symbols from the db.
        :param tickers: tickers of the symbols
        :return: Symbol information or False if none were found.
        """
        raise NotImplemented

    @abstractmethod
    def get_all_symbols(self, symbol_type: Literal['stock', 'index', 'all'] = 'all') \
            -> tuple[dict, ...]:
        """
        Gets all the symbols from the db.
        :param symbol_type: Filter by symbols type.
        :return: All symbols info that match the filter or empty tuple if none were found.
        """
        raise NotImplemented

    @abstractmethod
    def clean_old_symbols(self) -> None:
        """
        Finds symbols not updated and cleans it.
        """
        raise NotImplemented

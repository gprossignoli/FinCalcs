from abc import ABCMeta, abstractmethod
from typing import Union

from src.Symbol.domain.symbol import Symbol, SymbolInformation


class RepositoryInterface(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'save_symbol') and
                callable(subclass.save_symbol) and
                hasattr(subclass, 'get_symbol') and
                callable(subclass.get_symbol) and
                hasattr(subclass, 'clean_old_symbols') and
                callable(subclass.clean_old_symbols)
                ) or NotImplemented

    @abstractmethod
    def save_symbol(self, symbol: Symbol) -> None:
        """
        Save a symbol entity into the db
        """
        raise NotImplemented

    @abstractmethod
    def get_symbol(self, ticker: str) -> Union[SymbolInformation, bool]:
        """
        Gets the symbol from the db.
        :param ticker: ticker of the symbol
        :return: Symbol information or False if none were found.
        """
        raise NotImplemented

    @abstractmethod
    def get_symbols(self, tickers: tuple[str, ...]) -> Union[tuple[SymbolInformation, ...], bool]:
        """
        Gets the symbols from the db.
        :param tickers: tickers of the symbols
        :return: Symbol information or False if none were found.
        """
        raise NotImplemented

    @abstractmethod
    def clean_old_symbols(self) -> None:
        """
        Finds symbols not updated and cleans it.
        """
        raise NotImplemented

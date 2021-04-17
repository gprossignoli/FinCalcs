import queue

from src.Symbol.application.rabbitmq_consumer import RabbitmqConsumer
from src.Symbol.domain.ports.service_interface import ServiceInterface
from src.Symbol.domain.ports.repository_interface import RepositoryInterface
from src.Symbol.domain.symbol import Symbol, Index
from src.Utils.exceptions import DataConsumerException, DomainServiceException, RepositoryException
from src import settings as st


class MessageNotValid(Exception):
    pass


class FlaskServiceAdapter(ServiceInterface):
    def __init__(self, repository: RepositoryInterface = None):
        super().__init__()
        self.repository = repository

    def get_symbols_info(self) -> tuple[dict, ...]:
        """
        Obtains all symbols ticker, isin and name.
        """
        symbols = self.repository.get_all_symbols()
        ret = []
        for s in symbols:
            ret.append({'ticker': s.ticker,
                        'isin': s.isin,
                        'name': s.name})
        return tuple(ret)

    def get_symbol(self, symbol_ticker: str):
        symbol = self.repository.get_symbol(ticker=symbol_ticker)
        return {'ticker': symbol.ticker, 'isin': symbol.isin, 'name': symbol.name,
                'historic_data': {'closures': symbol.closures, 'daily_returns': symbol.daily_returns}}

    def get_symbol_with_statistics(self, symbol_ticker: str):
        symb_data = self.repository.get_symbol(ticker=symbol_ticker)
        symbol = self.create_symbol_entity(ticker=symb_data.ticker, isin=symb_data.isin,
                                           name=symb_data.name, closes=symb_data.closures,
                                           daily_returns=symb_data.daily_returns, dividends=symb_data.dividends)
        cagr_3yr = symbol.cagr(period='3yr')
        cagr_5yr = symbol.cagr(period='5yr')
        return {'ticker': symbol.ticker, 'isin': symbol.isin, 'name': symbol.name,
                'historic_data': {'closures': symbol.closures, 'daily_returns': symbol.daily_returns},
                'cagr': {'3yr': cagr_3yr, '5yr': cagr_5yr}}

    def create_symbol_entity(self, ticker: str, isin: str, name: str, closes: dict, dividends: dict,
                             daily_returns: dict) -> Symbol:
        return Symbol(ticker=ticker, isin=isin, name=name, historical_data={'close': closes, 'dividends': dividends,
                                                                            'daily_returns': daily_returns})

    def create_index_entity(self, ticker: str, isin: str, name: str, historic_data: dict) -> Symbol:
        return Index(ticker=ticker, isin=isin, name=name, historical_data=historic_data)

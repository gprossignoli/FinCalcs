from typing import Union

from src.Symbol.domain.ports.driver_service_interface import DriverServiceInterface
from src.Symbol.domain.ports.repository_interface import RepositoryInterface
from src.Symbol.domain.domain_service import DomainService, StockTransfer, StockInformationTransfer, \
    SymbolStatisticsTransfer, SymbolInformationTransfer
from src.Symbol.domain.symbol import Stock


class FlaskServiceAdapter(DriverServiceInterface):
    def __init__(self, repository: RepositoryInterface, domain_service: DomainService):
        super().__init__(repository=repository, domain_service=domain_service)

    def get_symbol(self, symbol_ticker: str) -> Union[SymbolStatisticsTransfer, bool]:
        symbol_data = self.repository.get_symbol(ticker=symbol_ticker)
        if not symbol_data:
            return False

        symbol = self.domain_service.create_symbol_entity(ticker=symbol_data['ticker'], isin=symbol_data.get('isin'),
                                                          name=symbol_data['name'], closures=symbol_data['closures'],
                                                          exchange=symbol_data.get('exchange'),
                                                          daily_returns=symbol_data.get('daily_returns'),
                                                          dividends=symbol_data.get('dividends'))

        cagr = {'3yr': self.domain_service.compute_cagr(symbol, period='3yr'),
                '5yr': self.domain_service.compute_cagr(symbol, period='5yr')}

        if isinstance(symbol, Stock):
            return StockTransfer(ticker=symbol.ticker, isin=symbol.isin, name=symbol.name,
                                 closures=symbol.closures, daily_returns=symbol.daily_returns,
                                 dividends=symbol.dividends, first_date=symbol.first_date,
                                 last_date=symbol.last_date, cagr=cagr, exchange=symbol.exchange)

        return SymbolStatisticsTransfer(ticker=symbol.ticker, name=symbol.name,
                                        closures=symbol.closures, daily_returns=symbol.daily_returns,
                                        first_date=symbol.first_date, last_date=symbol.last_date,
                                        cagr=cagr)

    def get_stocks_info(self) -> tuple[StockInformationTransfer, ...]:
        stocks = self.repository.get_all_symbols(symbol_type='stock')
        ret = []
        for stock in stocks:
            last_price_data = list(stock['closures'].items())[0]
            last_return_data = list(stock['daily_returns'].items())[0]
            ret.append(StockInformationTransfer(ticker=stock['ticker'], isin=stock['isin'], name=stock['name'],
                                                exchange=stock['exchange'],
                                                last_price={'date': last_price_data[0], 'value': last_price_data[1]},
                                                last_return={'date': last_return_data[0], 'value': last_price_data[1]}))
        return tuple(ret)

    def get_indexes_info(self) -> tuple[SymbolInformationTransfer, ...]:
        indexes = self.repository.get_all_symbols(symbol_type='index')
        ret = []
        for index in indexes:
            if not index:
                ret.append(False)
            last_price_data = list(index['closures'].items())[0]
            last_return_data = list(index['daily_returns'].items())[0]
            ret.append(SymbolInformationTransfer(ticker=index['ticker'], name=index['name'],
                                                 last_price={'date': last_price_data[0], 'value': last_price_data[1]},
                                                 last_return={'date': last_return_data[0], 'value': last_price_data[1]}))
        return tuple(ret)

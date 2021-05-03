import datetime

from src.Portfolio.domain.domain_service import DomainService, PortfolioStatisticsTransfer
from src.Portfolio.domain.portfolio import Portfolio
from src.Portfolio.domain.ports.driver_service_interface import DriverServiceInterface
from src.Symbol.domain.domain_service import DomainService as SymbolDomainService
from src.Symbol.domain.ports.repository_interface import RepositoryInterface as SymbolRepositoryInterface
from src.Utils.exceptions import PortfolioException
from src import settings as st


class FlaskServiceAdapter(DriverServiceInterface):
    def __init__(self, symbol_repository: SymbolRepositoryInterface, domain_service: DomainService,
                 symbol_domain_service: SymbolDomainService):
        super().__init__(symbol_repository=symbol_repository, domain_service=domain_service,
                         symbol_domain_service=symbol_domain_service)

    def create_portfolio(self, tickers: tuple[str], n_shares_per_symbol: dict[str, int],
                         initial_date: datetime.date, end_date: datetime.date) -> PortfolioStatisticsTransfer:
        if any(tickers) in st.EXCHANGES:
            raise PortfolioException(error="Invalid ticker")

        symbols_data = self.symbol_repository.get_symbols(tickers=tickers)
        if not symbols_data:
            raise PortfolioException(error="No symbols found")

        symbols = []
        for symbol in symbols_data:
            symbols.append(self.symbol_domain_service.
                           create_symbol_entity(ticker=symbol['ticker'], isin=symbol['isin'],
                                                name=symbol['name'], closures=symbol['closures'],
                                                exchange=symbol.get('exchange'),
                                                daily_returns=symbol.get('daily_returns'),
                                                dividends=symbol.get('dividends')))
        portfolio = self.domain_service.create_portfolio_entity(symbols=tuple(symbols),
                                                                n_shares_per_symbols=n_shares_per_symbol,
                                                                initial_date=initial_date, end_date=end_date)
        statistics = self._compute_portfolio_statistics(portfolio)

        return PortfolioStatisticsTransfer(symbols=tuple(symbol.ticker for symbol in portfolio.symbols),
                                           first_date=portfolio.first_date, last_date=portfolio.last_date,
                                           total_shares=portfolio.total_shares, weights=portfolio.weights,
                                           returns=portfolio.weighted_returns.to_dict(),
                                           volatility=portfolio.weighted_returns.to_dict(),
                                           annualized_returns=statistics['annualized_returns'],
                                           annualized_volatility=statistics['annualized_volatility'],
                                           maximum_drawdown=statistics['mdd'],
                                           sharpe_ratio=statistics['sharpe_ratio'],
                                           sortino_ratio=statistics['sortino_ratio'],
                                           calmar_ratio=statistics['calmar_ratio'])

    def _compute_portfolio_statistics(self, entity: Portfolio):
        statistics = {'annualized_returns': float(entity.annualized_returns[0]),
                      'annualized_volatility': float(entity.annualized_volatility), 'mdd': entity.mdd,
                      'sortino_ratio': self._compute_sortino_ratio(entity),
                      'sharpe_ratio': self.domain_service.sharpe_ratio(entity),
                      'calmar_ratio': self.domain_service.calmar_ratio(entity),
                      }

        return statistics

    def _compute_sortino_ratio(self, entity: Portfolio):
        benchmarks = set()
        for symbol in entity.symbols:
            benchmark = getattr(symbol, "exchange")
            if benchmark is not None:
                benchmarks.add(benchmark)
        ratios = {}
        # if the symbols have not exchange, we will compare the portfolio against S&P500
        if not benchmarks:
            rets = self.symbol_repository.get_symbol(st.EXCHANGES[1])['daily_returns']
            ratios[st.EXCHANGES[1]] = self.domain_service.sortino_ratio(entity, benchmark_returns=rets)
        else:
            for benchmark in benchmarks:
                index_data = self.symbol_repository.get_symbol(benchmark)
                index = self.symbol_domain_service.create_symbol_entity(ticker=index_data['ticker'],
                                                                        name=index_data['name'],
                                                                        closures=index_data['closures'],
                                                                        daily_returns=index_data.get('daily_returns'),
                                                                        dividends=index_data.get('dividends'))

                ratios[benchmark] = self.domain_service.sortino_ratio(entity, benchmark_returns=index.daily_returns)

        return ratios

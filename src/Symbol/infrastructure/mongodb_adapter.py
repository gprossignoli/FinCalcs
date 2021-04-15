from copy import deepcopy
from datetime import datetime, timedelta
from typing import Union

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from src.Symbol.domain.ports.repository_interface import RepositoryInterface
from src.Symbol.domain.symbol import Symbol, SymbolInformation
from src.Utils.exceptions import RepositoryException
from src import settings as st


class MongoRepositoryAdapter(RepositoryInterface):

    __db_client = None

    def __init__(self):
        self.__connect_to_db()
        self.collection = self.__db_client['fincalcs']['symbols']

    def save_symbol(self, symbol: Symbol):
        st.logger.info("Updating symbol {}".format(symbol.ticker))

        historic_data = self.__historic_data_to_json(symbol)

        doc_filter = {'_id': symbol.ticker}
        doc_values = {"$set": {"isin": symbol.isin,
                               "name": symbol.name,
                               "date": datetime.utcnow(),
                               "historic_data": historic_data}}

        try:
            self.collection.update_one(filter=doc_filter, update=doc_values, upsert=True)
        except PyMongoError as e:
            st.logger.exception(e)
            st.logger.info("Symbol {} not updated due to an error".format(symbol.ticker))
            raise RepositoryException()
        else:
            st.logger.info("Symbol {} updated".format(symbol.ticker))

    def get_symbol(self, ticker: str) -> Union[SymbolInformation, bool]:
        try:
            data = self.collection.find_one({"_id": ticker})
        except PyMongoError as e:
            st.logger.exception(e)
            raise RepositoryException
        if data is None:
            return False

        return SymbolInformation(ticker=data['_id'], isin=data['isin'], name=data['name'],
                                 closures=data['historic_data']['closures'],
                                 dividends=data['historic_data']['dividends'],
                                 daily_returns=data['historic_data']['daily_returns'])

    def get_symbols(self, tickers: tuple[str, ...]) -> Union[tuple[SymbolInformation, ...], bool]:
        try:
            data = self.collection.find({"_id": {"$in": tickers}})
        except PyMongoError as e:
            st.logger.exception(e)
            raise RepositoryException
        if data is None:
            return False
        return tuple(SymbolInformation(ticker=symbol['_id'], isin=symbol['isin'], name=symbol['name'],
                                       closures=symbol['historic_data']['closures'],
                                       dividends=symbol['historic_data']['dividends'],
                                       daily_returns=symbol['historic_data']['daily_returns'])
                     for symbol in data)

    def get_all_symbols(self) -> Union[tuple[SymbolInformation, ...], bool]:
        try:
            data = self.collection.find({})
        except PyMongoError as e:
            st.logger.exception(e)
            raise RepositoryException
        if data is None:
            return False

        return tuple(SymbolInformation(ticker=symbol['_id'], isin=symbol['isin'], name=symbol['name'],
                                       closures=symbol['historic_data']['closures'],
                                       dividends=symbol['historic_data']['dividends'],
                                       daily_returns=symbol['historic_data']['daily_returns'])
                     for symbol in data)

    def clean_old_symbols(self) -> None:
        try:
            data = self.collection.find({})
        except PyMongoError as e:
            st.logger.exception(e)
            raise RepositoryException

        date_limit = datetime.utcnow().date() - timedelta(days=5)
        symbols_to_delete = []
        for symbol in data:
            if symbol['date'].date() < date_limit:
                symbols_to_delete.append(symbol['ticker'])

        if not symbols_to_delete:
            return
        try:
            st.logger("Cleaning symbols with tickers: {}".format(symbols_to_delete))
            self.collection.delete_many({"_id": {"$in": symbols_to_delete}})
        except PyMongoError as e:
            st.logger.exception(e)
            raise RepositoryException

    @staticmethod
    def __historic_data_to_json(symbol: Symbol) -> dict[str, dict]:
        historic_data = deepcopy(symbol.historical_data)
        formatted_indexes = tuple(idx.strftime("%Y-%m-%d") for idx in historic_data['closures'].index)

        historic_data['closures'].index = formatted_indexes
        historic_data['closures'] = historic_data['closures'].to_json()

        if historic_data.get('dividends') is not None:
            historic_data['dividends'].index = formatted_indexes
            historic_data['dividends'] = historic_data['dividends'].to_json()

        historic_data['daily_returns'] = deepcopy(symbol.daily_returns)
        historic_data['daily_returns'].index = formatted_indexes
        historic_data['daily_returns'] = historic_data['daily_returns'].to_json()

        return historic_data

    @classmethod
    def __connect_to_db(cls):
        """
        Singleton method to initialize mongo database object
        """
        if cls.__db_client is None:
            try:
                st.logger.info("Connecting to mongodb database.")
                cls.__db_client = MongoClient(f'mongodb://{st.MONGO_HOST}:{st.MONGO_PORT}/', connect=False)
                # Forces a connection status check
                cls.__db_client.server_info()
            except PyMongoError as e:
                st.logger.exception(e)
                raise RepositoryException()

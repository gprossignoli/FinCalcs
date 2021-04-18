from datetime import datetime, timedelta
from typing import Union, Literal

import ujson
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from src.Symbol.domain.symbol import Stock, Index
from src.Symbol.domain.ports.repository_interface import RepositoryInterface
from src.Utils.exceptions import RepositoryException
from src import settings as st


class MongoRepositoryAdapter(RepositoryInterface):

    __db_client = None

    def __init__(self):
        self.__connect_to_db()
        self.symbols_collection = self.__db_client['fincalcs']['symbols']

    def save_stock(self, stock: Stock):
        st.logger.info("Updating symbol {}".format(stock.ticker))

        doc_filter = {'_id': stock.ticker}
        doc_values = {"$set": {"isin": stock.isin,
                               "name": stock.name,
                               "date": datetime.utcnow(),
                               "closures": ujson.dumps(stock.closures.to_dict()),
                               "dividends": ujson.dumps(stock.dividends.to_dict()),
                               "daily_returns": ujson.dumps(stock.daily_returns.to_dict()),
                               "type": "stock"}}

        try:
            self.symbols_collection.update_one(filter=doc_filter, update=doc_values, upsert=True)
        except PyMongoError as e:
            st.logger.exception(e)
            st.logger.info("Symbol {} not updated due to an error".format(stock.ticker))
            raise RepositoryException()
        else:
            st.logger.info("Symbol {} updated".format(stock.ticker))

    def save_index(self, index: Index):
        st.logger.info("Updating index {}".format(index.ticker))

        doc_filter = {'_id': index.ticker}
        doc_values = {"$set": {"isin": index.isin,
                               "name": index.name,
                               "date": datetime.utcnow(),
                               "closures": index.closures.to_dict(),
                               "daily_returns": index.daily_returns.to_dict(),
                               "type": "index"}}

        try:
            self.symbols_collection.update_one(filter=doc_filter, update=doc_values, upsert=True)
        except PyMongoError as e:
            st.logger.exception(e)
            st.logger.info("Index {} not updated due to an error".format(index.ticker))
            raise RepositoryException()
        else:
            st.logger.info("Index {} updated".format(index.ticker))

    def get_symbol(self, ticker: str) -> Union[dict, bool]:
        try:
            data = self.symbols_collection.find_one({"_id": ticker})
        except PyMongoError as e:
            st.logger.exception(e)
            raise RepositoryException
        if data is None:
            return False

        ret = {'ticker': data['_id'], 'isin': data['isin'],
               'name': data['name'], 'closures': data['closures']}
        dividends = data.get('dividends')
        if dividends is not None:
            ret['dividends'] = dividends
        daily_returns = data.get('daily_returns')
        if daily_returns is not None:
            ret['daily_returns'] = daily_returns
        return ret

    def get_symbols(self, tickers: tuple[str, ...]) -> Union[tuple[dict, ...], bool]:
        try:
            data = self.symbols_collection.find({"_id": {"$in": tickers}})
        except PyMongoError as e:
            st.logger.exception(e)
            raise RepositoryException
        if data is None:
            return False

        symbols = list()
        for d in data:
            symbol_info = {'ticker': d['_id'], 'isin': d['isin'],
                           'name': d['name'], 'closures': d['closures']}
            dividends = d.get('dividends')
            if dividends is not None:
                symbol_info['dividends'] = dividends
            daily_returns = d.get('daily_returns')
            if daily_returns is not None:
                symbol_info['daily_returns'] = daily_returns

            symbols.append(symbol_info)

        return tuple(symbols)

    def get_all_symbols(self, symbol_type: Literal['stock', 'index', 'all'] = 'all') -> tuple[dict, ...]:
        query = {"type": symbol_type} if symbol_type != 'all' else {}
        try:
            data = self.symbols_collection.find(query)
        except PyMongoError as e:
            st.logger.exception(e)
            raise RepositoryException

        symbols = list()
        for d in data:
            symbol_info = {'ticker': d['_id'], 'isin': d['isin'],
                           'name': d['name'], 'closures': d['closures']}
            dividends = d.get('dividends')
            if dividends is not None:
                symbol_info['dividends'] = dividends
            daily_returns = d.get('daily_returns')
            if daily_returns is not None:
                symbol_info['daily_returns'] = daily_returns

            symbols.append(symbol_info)

        return tuple(symbols)

    def clean_old_symbols(self) -> None:
        try:
            data = self.symbols_collection.find({})
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
            self.symbols_collection.delete_many({"_id": {"$in": symbols_to_delete}})
        except PyMongoError as e:
            st.logger.exception(e)
            raise RepositoryException

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

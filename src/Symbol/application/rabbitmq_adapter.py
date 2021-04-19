import queue

from src.Symbol.application.rabbitmq_consumer import RabbitmqConsumer
from src.Symbol.domain.ports.driven_service_interface import DrivenServiceInterface
from src.Symbol.domain.domain_service import DomainService
from src.Symbol.domain.ports.repository_interface import RepositoryInterface
from src.Utils.exceptions import DataConsumerException, ServiceException, RepositoryException
from src import settings as st


class MessageNotValid(Exception):
    pass


class RabbitmqServiceAdapter(DrivenServiceInterface):
    def __init__(self, repository: RepositoryInterface, domain_service: DomainService):
        super().__init__(repository=repository, domain_service=domain_service)
        self.__consumers_queue = queue.Queue()
        self.consumer = self.__create_rabbit_consumer(rabbit_queue=st.SYMBOLS_QUEUE, exchange=st.SYMBOLS_EXCHANGE,
                                                      routing_key=st.SYMBOLS_TOPIC_ROUTING_KEY)
        self.repository = repository

    def fetch_symbol_data(self) -> None:
        """
        Gets the symbol data, converts it to a symbol entity,
        precalculates it's financials data, and saves into the db.
        """
        try:
            self.consumer.start_consumer()
        except DataConsumerException:
            raise ServiceException()

        while True:
            try:
                symbol_message = self.__consumers_queue.get(timeout=0.5)
            except queue.Empty:
                if not self.consumer.connected:
                    break
                continue
            else:
                try:
                    self.__process_symbol_data_message(symbol_message)
                except MessageNotValid:
                    continue

    def save_stock(self, stock_info: dict) -> None:
        closures = stock_info['historic']['close']
        dividends = stock_info['historic']['dividends']
        stock = self.domain_service.create_symbol_entity(ticker=stock_info['ticker'], isin=stock_info['isin'],
                                                         name=stock_info['name'], closures=closures,
                                                         exchange=stock_info['exchange'], dividends=dividends)
        try:
            self.repository.save_stock(stock)
        except RepositoryException:
            pass

    def save_index(self, index_info: dict) -> None:
        closures = index_info['historic']['close']
        index = self.domain_service.create_symbol_entity(ticker=index_info['ticker'], isin=index_info['isin'],
                                                         name=index_info['name'], closures=closures)
        try:
            self.repository.save_index(index)
        except RepositoryException:
            pass

    def __create_rabbit_consumer(self, rabbit_queue: str, exchange: str, routing_key: str) -> RabbitmqConsumer:
        return RabbitmqConsumer(messages_received_queue=self.__consumers_queue, rabbit_queue=rabbit_queue,
                                exchange=exchange, routing_key=routing_key)

    def __process_symbol_data_message(self, symbol_message: dict) -> None:
        validation = self.__validate_message_format(symbol_message)
        if not validation[0]:
            st.logger.error("Message from {} received with missing key: {}".format(st.SYMBOLS_QUEUE,
                                                                                   validation[1]))
            raise MessageNotValid()
        if symbol_message['routing_key'] == st.SYMBOLS_STOCK_ROUTING_KEY:
            self.save_stock(symbol_message)
        elif symbol_message['routing_key'] == st.SYMBOLS_INDEX_ROUTING_KEY:
            self.save_index(symbol_message)

    @staticmethod
    def __validate_message_format(symbol_message: dict) -> tuple[bool, str]:
        """
        Validates the received message format.
        :param symbol_message: Message received from the consumer.
        :return: True,None if message is valid, False,Missing_key if is not valid.
        """
        if symbol_message.get('routing_key') is None:
            symbol_message['routing_key'] = 'default'

        historic = symbol_message.get('historic')

        if symbol_message.get('ticker') is None:
            key_error = 'ticker'
        elif symbol_message.get('isin') is None:
            key_error = 'isin'
        elif symbol_message.get('name') is None:
            key_error = 'name'
        elif historic is None:
            key_error = 'historic'
        elif historic.get('close') is None:
            key_error = 'historic.close'
        elif symbol_message.get('routing_key') == st.SYMBOLS_STOCK_ROUTING_KEY and \
                historic.get('dividends') is None:
            key_error = 'historic.dividends'
        else:
            key_error = None

        return (True, None) if key_error is None else (False, key_error)

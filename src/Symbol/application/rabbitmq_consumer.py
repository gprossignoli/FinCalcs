import socket
import threading
import queue

import ujson as ujson
from pika import PlainCredentials, BlockingConnection, ConnectionParameters
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import ConnectionWrongStateError, AMQPConnectionError, AMQPChannelError

from src.Utils.exceptions import DataConsumerException
from src import settings as st


class RabbitmqConsumer:
    def __init__(self, messages_received_queue: queue.Queue, rabbit_queue: str,
                 exchange: str, routing_key: str):
        super().__init__()
        self.connection = None
        self.channel = None
        self.connected = False
        self.__rabbit_queue = rabbit_queue
        self.__rabbit_exchange = exchange
        self.__rabbit_routing_key = routing_key
        self.__queue = messages_received_queue

    def start_consumer(self):
        self.connection = self.connect()
        try:
            self.channel = self.__setup_consumer()
        except DataConsumerException as e:
            self.disconnect()
            raise e

        self.channel.basic_consume(on_message_callback=self.__on_message, queue=self.__rabbit_queue)
        thread = threading.Thread(target=self.channel.start_consuming)
        thread.start()

    def connect(self) -> BlockingConnection:
        """
        Opens the connection to rabbit.
        """

        credentials = PlainCredentials(username=st.RABBIT_USER, password=st.RABBIT_PASSW)
        try:
            connection = BlockingConnection(
                ConnectionParameters(host=st.RABBIT_HOST, port=st.RABBIT_PORT,
                                     virtual_host=st.RABBIT_VHOST, credentials=credentials,
                                     connection_attempts=5,
                                     retry_delay=3))
        except (AMQPConnectionError, socket.gaierror) as e:
            st.logger.exception(e)
            self.connected = False
            raise DataConsumerException()

        st.logger.info("Symbol rabbitmq consumer connected")
        self.connected = True
        return connection

    def disconnect(self):
        try:
            self.connection.close()
            st.logger.info("Symbol rabbitmq consumer disconnected")
        except ConnectionWrongStateError:
            pass
        finally:
            self.connected = False

    def __on_message(self, channel, basic_deliver, properties, body):
        message = ujson.loads(body)
        message['routing_key'] = basic_deliver.routing_key
        try:
            self.__queue.put(message, timeout=1)
        except queue.Full:
            st.logger.warning("Message for symbol: {} cannot be processed, "
                              "will be resent to the exchange".format(message.get('ticker', 'unknown ticker')))
            channel.basic_nack(delivery_tag=basic_deliver.delivery_tag)
        else:
            channel.basic_ack(delivery_tag=basic_deliver.delivery_tag)

    def __setup_consumer(self) -> BlockingChannel:
        retry = 0
        while retry < 3:
            try:
                channel = self.connection.channel()

                channel.exchange_declare(exchange=st.SYMBOLS_EXCHANGE, exchange_type='topic', durable=True)
                channel.queue_declare(queue=self.__rabbit_queue)
                channel.basic_qos(prefetch_count=1)
                channel.queue_bind(exchange=self.__rabbit_exchange, queue=self.__rabbit_queue,
                                   routing_key=self.__rabbit_routing_key)
            except AMQPChannelError as e:
                st.logger.exception(e)
                self.connected = False
                retry += 1
            else:
                self.connected = True
                return channel
        else:
            raise DataConsumerException()

import threading

from src.Symbol.domain.ports.use_case_interface import UseCaseInterface
from src.Symbol.domain.domain_service import DomainService
from src.Symbol.application.rabbitmq_adapter import RabbitmqServiceAdapter
from src.Symbol.infrastructure.mongodb_adapter import MongoRepositoryAdapter
from src.Utils.exceptions import ServiceException
from src import settings as st


class FetchSymbolsUseCase(UseCaseInterface):
    def execute(self):
        """
        This use case consumes events related to Symbols
        and creates all the related info with a symbol entity.
        """
        st.logger.info("Starting fetch symbols use case")
        try:
            rabbit_adapter = RabbitmqServiceAdapter(repository=MongoRepositoryAdapter(),
                                                    domain_service=DomainService())
            thread = threading.Thread(target=rabbit_adapter.fetch_symbol_data)
            thread.start()

        except ServiceException:
            st.logger.error("Fetch symbols use case error, service restart is required!")
            return

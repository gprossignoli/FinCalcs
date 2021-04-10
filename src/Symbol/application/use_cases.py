from src.Symbol.domain.ports.use_case_interface import UseCaseInterface
from src.Symbol.application.rabbitmq_adapter import RabbitmqServiceAdapter
from src.Symbol.infraestructure.mongodb_adapter import MongoRepositoryAdapter
from src.Utils.exceptions import DomainServiceException
from src import settings as st


class FetchSymbolsUseCase(UseCaseInterface):
    def execute(self):
        """
        This use case consumes events related to Symbols
        and creates all the related info with a symbol entity.
        """
        st.logger.info("Initiating fetch symbols use case")
        try:
            RabbitmqServiceAdapter(repository=MongoRepositoryAdapter()).fetch_symbol_data()
        except DomainServiceException:
            st.logger.error("Fetch symbols use case error, service restart is required!")
            return

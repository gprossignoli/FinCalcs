class DataConsumerException(Exception):
    pass


class ServiceException(Exception):
    pass


class RepositoryException(Exception):
    pass


class PortfolioException(Exception):
    def __init__(self, error: str):
        super(PortfolioException, self).__init__()
        self.error = error

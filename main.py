import time

from src.Symbol.application.use_cases import FetchSymbolsUseCase
from src.api import start_api

if __name__ == '__main__':

    FetchSymbolsUseCase().execute()
    start_api()
    while True:
        time.sleep(60)
        pass


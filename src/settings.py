import os
import logging
from logging.handlers import RotatingFileHandler

from environ import environ

ROOT_DIR = os.path.dirname(os.path.dirname((os.path.abspath(__file__))))
ENV_FILE = os.path.abspath(os.path.join(ROOT_DIR, ".env"))

env = environ.Env(
    MONGO_DB=(str, ""),
    MONGODB_USER=(str, ""),
    MONGODB_PASS=(str, ""),
    RABBIT_HOST=(str, ""),
    RABBIT_PORT=(int, None),
    RABBIT_USER=(str, ""),
    RABBIT_PASSWORD=(str, ""),
    RABBIT_VHOST=(str, ""),
)

env.read_env(ENV_FILE)

MONGO_HOST, MONGO_PORT = env("MONGO_DB").split(":")

# LOGGING CONFIG

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('fincalcs')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# to log debug messages
debug_logger = logging.StreamHandler()
debug_logger.setLevel(logging.DEBUG)
debug_logger.setFormatter(formatter)

# to log general messages
# x2 files of 2mb
info_logger = RotatingFileHandler(filename='fincalcs.log', maxBytes=2097152, backupCount=2)
info_logger.setLevel(logging.INFO)
info_logger.setFormatter(formatter)

# to log errors messages
error_logger = RotatingFileHandler(filename='fincalcs_errors.log', maxBytes=2097152, backupCount=2)
error_logger.setLevel(logging.ERROR)
error_logger.setFormatter(formatter)

logger.addHandler(debug_logger)
logger.addHandler(info_logger)
logger.addHandler(error_logger)

# Rabbitmq data
RABBIT_HOST = env("RABBIT_HOST")
RABBIT_PORT = env("RABBIT_PORT")
RABBIT_USER = env("RABBIT_USER")
RABBIT_PASSW = env("RABBIT_PASSWORD")
RABBIT_VHOST = env("RABBIT_VHOST")

SYMBOLS_EXCHANGE = 'findata_symbols'
SYMBOLS_EXCHANGE_TYPE = 'topic'
SYMBOLS_QUEUE = 'fincalcs_symbols'
SYMBOLS_TOPIC_ROUTING_KEY = 'findata.symbol.#'
SYMBOLS_STOCK_ROUTING_KEY = 'findata.symbol.stock'
SYMBOLS_INDEX_ROUTING_KEY = 'findata.symbol.index'

# Ibex35, S&P500, Dow Jones, Nasdaq, Euro stoxx50, EURONEXT100, Ibex Medium Cap.
EXCHANGES = ('^IBEX', '^GSPC', '^DJI', '^IXIC', '^STOXX50E', '^N100', 'INDC.MC')

# Is commonly accepted that there are 252 trading days in the year.
ANNUALIZATION_FACTOR = 252
# We assume a 2%
RISK_FREE_RATIO = 0.02

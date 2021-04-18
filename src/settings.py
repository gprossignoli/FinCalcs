import logging
import os
import configparser
from logging.handlers import RotatingFileHandler

ROOT_DIR = os.path.dirname(os.path.dirname((os.path.abspath(__file__))))
settings_file = open(os.path.join(ROOT_DIR, "settings.ini"), "r")
config = configparser.ConfigParser()
config.read(os.path.join(ROOT_DIR, "settings.ini"))

MONGO_HOST, MONGO_PORT = config.get("DB", "mongo_db").split(":")


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
RABBIT_HOST = config.get("RABBIT", "rabbit_host")
RABBIT_PORT = config.get("RABBIT", "rabbit_port")
RABBIT_USER = config.get("RABBIT", "rabbit_user")
RABBIT_PASSW = config.get("RABBIT", "rabbit_password")
RABBIT_VHOST = config.get("RABBIT", "rabbit_vhost")

SYMBOLS_EXCHANGE = 'findata_symbols'
SYMBOLS_EXCHANGE_TYPE = 'topic'
SYMBOLS_QUEUE = 'fincalcs_symbols'
SYMBOLS_TOPIC_ROUTING_KEY = 'findata.symbol.#'
SYMBOLS_STOCK_ROUTING_KEY = 'findata.symbol.stock'
SYMBOLS_INDEX_ROUTING_KEY = 'findata.symbol.index'


# Ibex35, S&P500, Dow Jones, Nasdaq, Euro stoxx50, EURONEXT100.
EXCHANGES = ('^IBEX', '^GSPC', '^DJI', '^IXIC', '^STOXX50E', '^N100')

# Is commonly accepted that there are 252 trading days in the year.
ANNUALIZATION_FACTOR = 252
# We assume a 2%
RISK_FREE_RATIO = 0.02

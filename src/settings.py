import logging
import os
import configparser
from logging.handlers import RotatingFileHandler

ROOT_DIR = os.path.dirname(os.path.abspath("settings.py"))
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
SYMBOLS_ROUTING_KEY = 'findata.symbol'

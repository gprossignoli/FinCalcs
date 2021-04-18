import ujson
from flask import Blueprint, Response

from src.Symbol.application.flask_adapter import FlaskServiceAdapter
from src.Symbol.domain.domain_service import DomainService
from src.Symbol.infrastructure.mongodb_adapter import MongoRepositoryAdapter
symbols = Blueprint(name='symbols', import_name=__name__, url_prefix='/symbols')


symbol_service = FlaskServiceAdapter(repository=MongoRepositoryAdapter(), domain_service=DomainService())


@symbols.route('/stocks', methods=['GET'])
def get_stocks_list():
    symbs = ujson.dumps(symbol_service.get_stocks_info())
    return Response(response=symbs, status=200, mimetype='application/json')


@symbols.route('/indexes', methods=['GET'])
def get_indexes_list():
    symbs = ujson.dumps(symbol_service.get_indexes_info())
    return Response(response=symbs, status=200, mimetype='application/json')


@symbols.route('/<symbol_ticker>', methods=['GET'])
def get_symbol(symbol_ticker):
    symbol = ujson.dumps(symbol_service.get_symbol(symbol_ticker))
    return Response(response=symbol, status=200, mimetype='application/json')

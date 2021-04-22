import ujson
from flask import Blueprint, Response, request
from cerberus.validator import Validator
from cerberus.errors import ValidationError

from src.Portfolio.application.flask_adapter import FlaskServiceAdapter
from src.Portfolio.domain.domain_service import DomainService
from src.Symbol.domain.domain_service import DomainService as SymbolDomainService
from src.Symbol.infrastructure.mongodb_adapter import MongoRepositoryAdapter


portfolio_blueprint = Blueprint(name='portfolio', import_name=__name__, url_prefix='/portfolio')


portfolio_service = FlaskServiceAdapter(symbol_repository=MongoRepositoryAdapter(),
                                        symbol_domain_service=SymbolDomainService(),
                                        domain_service=DomainService())


@portfolio_blueprint.route('', methods=['POST'])
def get_portfolio_analysis():
    schema = {
        'tickers': {
            'type': 'list',
            'schema': {'type': 'string', 'min': 0},
            'nullable': False,
            'empty': False
        }
    }

    body = {'tickers': [ticker.strip() for ticker in request.form.get('tickers').split(",")]}
    shares_per_stock = {}
    input = request.form.get('sharesPerStock').split(",")
    for stock in input:
        s = stock.split(":")
        shares_per_stock[s[0]] = int(s[1])
    body['shares_per_stock'] = shares_per_stock
    try:
        v = Validator(schema=schema)
        v.allow_unknown = True
        val = v.validate(body, schema)
    except ValidationError as e:
        return Response(response='Invalid request: tickers not valid', status=400,
                        mimetype='application/json')

    if not val:
        return Response(response='Invalid request: tickers not valid', status=400,
                        mimetype='application/json')

    portfolio_info = (portfolio_service.create_portfolio(tickers=tuple(body['tickers']),
                                                         n_shares_per_symbol=body['shares_per_stock']))

    return Response(response=ujson.dumps(portfolio_info.to_json()), status=200, mimetype='application/json')

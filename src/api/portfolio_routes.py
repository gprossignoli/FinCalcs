import ujson
from flask import Blueprint, Response, request
from cerberus.validator import Validator
from cerberus.errors import ValidationError

from src.Portfolio.application.flask_adapter import FlaskServiceAdapter
from src.Portfolio.domain.domain_service import DomainService
from src.Symbol.domain.domain_service import DomainService as SymbolDomainService
from src.Symbol.infrastructure.mongodb_adapter import MongoRepositoryAdapter
from src.Utils.exceptions import PortfolioException

portfolio_blueprint = Blueprint(name='portfolio', import_name=__name__, url_prefix='/portfolio')


portfolio_service = FlaskServiceAdapter(symbol_repository=MongoRepositoryAdapter(),
                                        symbol_domain_service=SymbolDomainService(),
                                        domain_service=DomainService())


@portfolio_blueprint.route('', methods=['POST'])
def get_portfolio_analysis():
    schema = {
        'tickers': {
            'type': 'list',
            'schema': {'type': 'string', 'min': 1},
            'nullable': False,
            'empty': False
        }
    }
    data = request.data if len(request.data) > 0 else request.form
    data = ujson.loads(data)
    body = {'tickers': [ticker.strip() for ticker in data.get('tickers').split(",")]}
    shares_per_stock = {}
    sps_input = data.get('sharesPerStock').split(",")
    for stock in sps_input:
        s = stock.split(":")
        shares_per_stock[s[0].strip()] = int(s[1])
    body['shares_per_stock'] = shares_per_stock
    try:
        v = Validator(schema=schema)
        v.allow_unknown = True
        val = v.validate(body, schema)
        tickers = body['tickers']
        shares_per_stock = list(body['shares_per_stock'].keys())

        if len(tickers) != len(shares_per_stock):
            return Response(response="Invalid request: number of tickers not equals "
                                     "to number of shares_per_stock's keys indicated", status=400,
                            mimetype='application/json')
        if tickers != shares_per_stock:
            return Response(response="Invalid request: Tickers and shares_per_stock's keys should match.", status=400,
                            mimetype='application/json')

    except ValidationError as e:
        return Response(response='Invalid request: tickers not valid', status=400,
                        mimetype='application/json')

    if not val:
        return Response(response='Invalid request: tickers not valid', status=400,
                        mimetype='application/json')

    try:
        portfolio_info = (portfolio_service.create_portfolio(tickers=tuple(body['tickers']),
                                                             n_shares_per_symbol=body['shares_per_stock']))
    except PortfolioException as e:
        if e.error == 'No symbols found':
            return Response(response=ujson.dumps(e.error), status=404, mimetype='application/json')
        elif e.error == 'Invalid ticker':
            return Response(response=ujson.dumps(e.error), status=400, mimetype='application/json')
    else:
        return Response(response=ujson.dumps(portfolio_info.to_json()), status=200, mimetype='application/json')

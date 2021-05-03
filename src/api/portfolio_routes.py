from datetime import datetime

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
    def to_date(d):
        return datetime.strptime(d, '%d-%m-%Y').date()

    schema = {
        'tickers': {
            'type': 'list',
            'schema': {'type': 'string', 'min': 1},
            'nullable': False,
            'empty': False
        },
        'initial_date': {'type': 'date', 'coerce': to_date, 'required': False},
        'end_date': {'type': 'date', 'coerce': to_date, 'required': False}
    }
    data = request.data if len(request.data) > 0 else request.form
    try:
        data = ujson.loads(data)
    except TypeError as e:
        pass

    body = {'tickers': [ticker.strip() for ticker in data.get('tickers').split(",")]}
    initial_date = data.get('initial_date')
    end_date = data.get('end_date')
    if initial_date is not None:
        body['initial_date'] = initial_date
    if end_date is not None:
        body['end_date'] = end_date

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

        if not val:
            return Response(response="Invalid request: {}".format(ujson.dumps(v.errors)), status=400,
                            mimetype='application/json')

        body = v.normalized(body)
        tickers = body['tickers']
        shares_per_stock = list(body['shares_per_stock'].keys())

        if len(tickers) != len(shares_per_stock):
            return Response(response="Invalid request: number of tickers not equals "
                                     "to number of shares_per_stock's keys indicated", status=400,
                            mimetype='application/json')
        if tickers != shares_per_stock:
            return Response(response="Invalid request: Tickers and shares_per_stock's keys should match.", status=400,
                            mimetype='application/json')

        if body['initial_date'] >= body['end_date']:
            return Response(response="Invalid request: Initial Date must be previous to End Date.", status=400,
                            mimetype='application/json')
    except ValidationError as e:
        return Response(response='Invalid request: tickers not valid', status=400,
                        mimetype='application/json')

    try:
        portfolio_info = (portfolio_service.create_portfolio(tickers=tuple(body['tickers']),
                                                             n_shares_per_symbol=body['shares_per_stock'],
                                                             initial_date=body['initial_date'],
                                                             end_date=body['end_date']))
    except PortfolioException as e:
        if e.error == 'No symbols found':
            return Response(response=ujson.dumps(e.error), status=404, mimetype='application/json')
        elif e.error == 'Invalid ticker':
            return Response(response=ujson.dumps(e.error), status=400, mimetype='application/json')
    else:
        return Response(response=ujson.dumps(portfolio_info.to_json()), status=200, mimetype='application/json')

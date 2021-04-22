from flask import Flask

from src.api.portfolio_routes import portfolio_blueprint
from src.api.symbol_routes import symbols as symbols_blueprint


app = Flask(__name__)
app.register_blueprint(symbols_blueprint)
app.register_blueprint(portfolio_blueprint)


def start_api():
    app.run(host='0.0.0.0', port=8001)



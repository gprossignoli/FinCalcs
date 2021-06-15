# FinCalcs
Application, part of my final degree's project, that consumes financial data by using RabbitMQ (Check https://github.com/gprossignoli/findata) and performs various financial calculations and provides them through an api.


The API has two resources:
- Symbols: Which serves the information for symbols as stocks or market indexes.
  - GET /symbols/stocks returns a list for all available stocks.
  - GET /symbols/indexes returns a list for all available market indexes.
  - GET /symbols/symbol_ticker> returns the details of a specific symbol.
- Portfolios: Which covers the building and analysis of Portfolios.
  - POST /portfolio validates the user input, and returns the analysis of the Portfolio.
  

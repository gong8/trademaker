from flask import Flask, request
from numpy import float32
from requests import HTTPError
from status import STATUS
from polygon import get_data
from helper import get_param, standard_rulebook, parse_date, parse_candlesticks, ewan_rulebook
from calc import simulate_detail

app = Flask(__name__)

@app.route('/api/get_data', methods=['GET'])
def get_data_endpoint():
  args = request.args
  try:
    ticker = get_param(args, "ticker", "Ticker", str)
    multiplier = get_param(args, "multiplier", "Multiplier", int)
    timespan = get_param(args, "timespan", "Timespan", str)
    from_date = parse_date(get_param(args, "from", "From Date", str))
    to_date = parse_date(get_param(args, "to", "To Date", str))
  except ValueError as error:
    return str(error), STATUS.BAD_REQUEST
  try:
    data = get_data(ticker, multiplier, timespan, from_date, to_date)
  except HTTPError as error:
    return str(error), STATUS.POLYGON_ERROR
  return data, STATUS.OK
  
@app.route('/api/simulate', methods=['GET'])
def simulate_endpoint():
  args = request.args
  try:
    initial_stock = get_param(args, "initialStock", "Initial Stock", float32)
    initial_wallet = get_param(args, "initialWallet", "Initial Wallet", float32)
    ticker = get_param(args, "ticker", "Ticker", str)
    multiplier = get_param(args, "multiplier", "Multiplier", int)
    timespan = get_param(args, "timespan", "Timespan", str)
    from_date = parse_date(get_param(args, "from", "From Date", str))
    to_date = parse_date(get_param(args, "to", "To Date", str))
  except ValueError as error:
    return str(error), STATUS.BAD_REQUEST
  try:
    str_data = get_data(ticker, multiplier, timespan, from_date, to_date)
  except HTTPError as error:
    return str(error), STATUS.POLYGON_ERROR
  candlesticks = parse_candlesticks(str_data)
  try:
    result = simulate_detail(
      candlesticks,
      ewan_rulebook,
      initial_stock / candlesticks[0],
      initial_wallet,
      1,
      2,
      10
    )
  except RuntimeError as error:
    return str(error), STATUS.SIMULATOR_ERROR
  return str(list(map(list, result))), STATUS.OK

if __name__ == '__main__':
  app.run(port = 5000)
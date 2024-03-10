from flask import Flask, request
from numpy import float32
from requests import HTTPError
from status import STATUS
from polygon import get_data
from helper import get_param, create_rulebook, Candle, Attribute, Bound, parse_date, parse_candlesticks
from calc import simulate

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
  rulebook = create_rulebook(
    [float32(0.1), float32(-0.1)],
    3,
    [
      # bear
      (0, (Candle.FIRST, Attribute.CLOSE, Bound.UPPER), (Candle.FIRST, Attribute.OPEN), float32(1)),
      (0, (Candle.FIRST, Attribute.CLOSE, Bound.UPPER), (Candle.CONSTANT, Attribute.CONSTANT), float32(0)),
      
      # bear
      (0, (Candle.SECOND, Attribute.CLOSE, Bound.UPPER), (Candle.SECOND, Attribute.OPEN), float32(1)),
      (0, (Candle.SECOND, Attribute.CLOSE, Bound.UPPER), (Candle.CONSTANT, Attribute.CONSTANT), float32(0)),
      
      # bull
      (0, (Candle.THIRD, Attribute.CLOSE, Bound.LOWER), (Candle.THIRD, Attribute.OPEN), float32(1)),
      (0, (Candle.THIRD, Attribute.CLOSE, Bound.LOWER), (Candle.CONSTANT, Attribute.CONSTANT), float32(0)),

      # third close < ema
      (0, (Candle.THIRD, Attribute.CLOSE, Bound.UPPER), (Candle.EMA, Attribute.EMA), float32(1)),

      # third above first
      (0, (Candle.FIRST, Attribute.HIGH, Bound.UPPER), (Candle.THIRD, Attribute.CLOSE), float32(1)),      
      (0, (Candle.FIRST, Attribute.HIGH, Bound.UPPER), (Candle.CONSTANT, Attribute.CONSTANT), float32(0)),

      # third above second
      (0, (Candle.SECOND, Attribute.HIGH, Bound.UPPER), (Candle.THIRD, Attribute.CLOSE), float32(1)),
      (0, (Candle.SECOND, Attribute.HIGH, Bound.UPPER), (Candle.CONSTANT, Attribute.CONSTANT), float32(0)),

      # -----------------------------

      # bull
      (1, (Candle.FIRST, Attribute.CLOSE, Bound.LOWER), (Candle.FIRST, Attribute.OPEN), float32(1)),
      (1, (Candle.FIRST, Attribute.CLOSE, Bound.LOWER), (Candle.CONSTANT, Attribute.CONSTANT), float32(0)),
      
      # bull
      (1, (Candle.SECOND, Attribute.CLOSE, Bound.LOWER), (Candle.SECOND, Attribute.OPEN), float32(1)),
      (1, (Candle.SECOND, Attribute.CLOSE, Bound.LOWER), (Candle.CONSTANT, Attribute.CONSTANT), float32(0)),
      
      # bear
      (1, (Candle.THIRD, Attribute.CLOSE, Bound.UPPER), (Candle.THIRD, Attribute.OPEN), float32(1)),
      (1, (Candle.THIRD, Attribute.CLOSE, Bound.UPPER), (Candle.CONSTANT, Attribute.CONSTANT), float32(0)),

      # third close < ema
      (1, (Candle.THIRD, Attribute.CLOSE, Bound.LOWER), (Candle.EMA, Attribute.EMA), float32(1)),

      # third above first
      (1, (Candle.FIRST, Attribute.HIGH, Bound.LOWER), (Candle.THIRD, Attribute.CLOSE), float32(1)),      
      (1, (Candle.FIRST, Attribute.HIGH, Bound.LOWER), (Candle.CONSTANT, Attribute.CONSTANT), float32(0)),

      # third above second
      (1, (Candle.SECOND, Attribute.HIGH, Bound.LOWER), (Candle.THIRD, Attribute.CLOSE), float32(1)),
      (1, (Candle.SECOND, Attribute.HIGH, Bound.LOWER), (Candle.CONSTANT, Attribute.CONSTANT), float32(0)),
    ]
  )
  try:
    str_data = get_data(ticker, multiplier, timespan, from_date, to_date)
  except HTTPError as error:
    return str(error), STATUS.POLYGON_ERROR
  candlesticks = parse_candlesticks(str_data)
  try:
    result = simulate(
      candlesticks,
      rulebook,
      initial_stock / candlesticks[0],
      initial_wallet,
      3,
      2,
      10
    )
  except RuntimeError as error:
    return str(error), STATUS.SIMULATOR_ERROR
  return str(result), STATUS.OK
  


if __name__ == '__main__':
  app.run(port = 5000)
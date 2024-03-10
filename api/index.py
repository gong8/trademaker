from flask import Flask, request
from requests import HTTPError
from status import STATUS
from polygon import get_data
from utils import create_rulebook, Candle, Attribute, Bound, parse_date, parse_candlesticks
from calc import simulate

app = Flask(__name__)

@app.route('/api/get_data', methods=['GET'])
def get_data_endpoint():
  args = request.args
  ticker = args.get("ticker")
  multiplier = args.get("multiplier", None, int)
  timespan = args.get("timespan")
  from_date = args.get("from")
  to_date = args.get("to")
  for var, name in [
    [ticker, "Ticker"],
    [multiplier, "Multiplier"], 
    [timespan, "Timespan"], 
    [from_date, "From"],
    [to_date, "To"]
  ]:
    if not var:
      return f"{name} not specified", STATUS.BAD_REQUEST
  try:
    data = get_data(ticker, multiplier, timespan, parse_date(from_date), parse_date(to_date))
  except HTTPError as error:
    return str(error), STATUS.POLYGON_ERROR
  return data, STATUS.OK

@app.route('/api/simulate', methods=['GET'])
def simulate_endpoint():
  args = request.args
  initial_stock = args.get("initialStock")
  initial_wallet = args.get("initialWallet")
  ticker = args.get("ticker")
  multiplier = args.get("multiplier")
  timespan = args.get("timespan")
  from_date = args.get("from")
  to_date = args.get("to")
  
  for var, name in [
      [initial_stock, "Initial Stock"],
      [initial_wallet, "Initial Wallet"],
      [ticker, "Ticker"],
      [multiplier, "Multiplier"],
      [timespan, "Timespan"],
      [from_date, "From Date"],
      [to_date, "To Date"]
    ]:
      if not var:
        return f"{name} not specified", STATUS.BAD_REQUEST
  
  rulebook = create_rulebook(
    [0.1, -0.1],
    3,
    [
      # bear
      (0, (Candle.FIRST, Attribute.CLOSE, Bound.UPPER), (Candle.FIRST, Attribute.OPEN), 1),
      (0, (Candle.FIRST, Attribute.CLOSE, Bound.UPPER), (Candle.CONSTANT, Attribute.CONSTANT), 0),
      
      # bear
      (0, (Candle.SECOND, Attribute.CLOSE, Bound.UPPER), (Candle.SECOND, Attribute.OPEN), 1),
      (0, (Candle.SECOND, Attribute.CLOSE, Bound.UPPER), (Candle.CONSTANT, Attribute.CONSTANT), 0),
      
      # bull
      (0, (Candle.THIRD, Attribute.CLOSE, Bound.LOWER), (Candle.THIRD, Attribute.OPEN), 1),
      (0, (Candle.THIRD, Attribute.CLOSE, Bound.LOWER), (Candle.CONSTANT, Attribute.CONSTANT), 0),

      # third close < ema
      (0, (Candle.THIRD, Attribute.CLOSE, Bound.UPPER), (Candle.EMA, Attribute.EMA), 1),

      # third above first
      (0, (Candle.FIRST, Attribute.HIGH, Bound.UPPER), (Candle.THIRD, Attribute.CLOSE), 1),      
      (0, (Candle.FIRST, Attribute.HIGH, Bound.UPPER), (Candle.CONSTANT, Attribute.CONSTANT), 0),

      # third above second
      (0, (Candle.SECOND, Attribute.HIGH, Bound.UPPER), (Candle.THIRD, Attribute.CLOSE), 1),
      (0, (Candle.SECOND, Attribute.HIGH, Bound.UPPER), (Candle.CONSTANT, Attribute.CONSTANT), 0),

      # -----------------------------

      # bull
      (1, (Candle.FIRST, Attribute.CLOSE, Bound.LOWER), (Candle.FIRST, Attribute.OPEN), 1),
      (1, (Candle.FIRST, Attribute.CLOSE, Bound.LOWER), (Candle.CONSTANT, Attribute.CONSTANT), 0),
      
      # bull
      (1, (Candle.SECOND, Attribute.CLOSE, Bound.LOWER), (Candle.SECOND, Attribute.OPEN), 1),
      (1, (Candle.SECOND, Attribute.CLOSE, Bound.LOWER), (Candle.CONSTANT, Attribute.CONSTANT), 0),
      
      # bear
      (1, (Candle.THIRD, Attribute.CLOSE, Bound.UPPER), (Candle.THIRD, Attribute.OPEN), 1),
      (1, (Candle.THIRD, Attribute.CLOSE, Bound.UPPER), (Candle.CONSTANT, Attribute.CONSTANT), 0),

      # third close < ema
      (1, (Candle.THIRD, Attribute.CLOSE, Bound.LOWER), (Candle.EMA, Attribute.EMA), 1),

      # third above first
      (1, (Candle.FIRST, Attribute.HIGH, Bound.LOWER), (Candle.THIRD, Attribute.CLOSE), 1),      
      (1, (Candle.FIRST, Attribute.HIGH, Bound.LOWER), (Candle.CONSTANT, Attribute.CONSTANT), 0),

      # third above second
      (1, (Candle.SECOND, Attribute.HIGH, Bound.LOWER), (Candle.THIRD, Attribute.CLOSE), 1),
      (1, (Candle.SECOND, Attribute.HIGH, Bound.LOWER), (Candle.CONSTANT, Attribute.CONSTANT), 0),
    ]
  )

  try:
    str_data = get_data(ticker, int(multiplier), timespan, parse_date(from_date), parse_date(to_date))
    candlesticks = parse_candlesticks(str_data)

    result = simulate(
      candlesticks,
      rulebook,
      float(initial_stock) / candlesticks[0] if candlesticks[0] != 0 else 0,
      float(initial_wallet),
      3,
      2,
      10
    )

    return str(result), STATUS.OK
  except RuntimeError as error:
    return str(error), STATUS.SIMULATOR_ERROR
  


if __name__ == '__main__':
  app.run(port = 5000)
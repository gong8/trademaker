from flask import Flask, request
from requests import HTTPError
from status import STATUS
from polygon import get_data
from utils import parse_date
import calc as c

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

if __name__ == '__main__':
  app.run(port = 5000)
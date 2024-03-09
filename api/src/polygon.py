from dotenv import load_dotenv
from datetime import datetime
from requests import get
from utils import str_date
from os import environ

load_dotenv()
API_KEY = environ.get("API_KEY")
BASE_URL = "https://api.polygon.io"
HEADERS = { "Authorization": f"Bearer {API_KEY}" }

def get_data(
  ticker: str, 
  multiplier: int, timespan: str, 
  from_date: datetime, to_date: datetime
) -> str:
  from_str = str_date(from_date)
  to_str = str_date(to_date)
  url = BASE_URL + f"/v1/indicators/ema/{ticker}/range/{multiplier}/{timespan}/{from_str}/{to_str}"
  response = get(url, headers=HEADERS)
  if not response.ok:
    response.raise_for_status()
  return response.text

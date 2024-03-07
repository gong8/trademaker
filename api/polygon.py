from dotenv import load_dotenv
from datetime import datetime
from requests import get
from os import environ

load_dotenv()
API_KEY = environ.get("API_KEY")
BASE_URL = "https://api.polygon.io/v2"
HEADERS = { "Authorization": f"Bearer {API_KEY}" }
DAY = 1000 * 60 * 60 * 24

def get_data(
  ticker: str, 
  multiplier: int, timespan: str, 
  from_date: datetime, to_date: datetime
) -> str:
  from_utc = int(from_date.timestamp() * 1000)
  to_utc = int(to_date.timestamp() * 1000 + DAY - 1)
  url = BASE_URL + f"/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_utc}/{to_utc}"
  response = get(url, headers=HEADERS)
  if not response.ok:
    response.raise_for_status()
  return response.text
   
  
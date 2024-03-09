from typing import List, Tuple
from datetime import datetime
from numpy import zeros, float32, array
import numpy.typing as npt
import re
import json

def parse_date(date_str: str) -> datetime:
  parts = re.split("[/\-]", date_str)
  if len(parts) != 3:
    raise RuntimeError("Invalid date format")
  year = int(parts[0])  
  month = int(parts[1])  
  day = int(parts[2])  
  return datetime(year, month, day)
  
def str_date(date: datetime) -> str:
  return f"{date.year}-{str(date.month).zfill(2)}-{str(date.day).zfill(2)}"

def parse_candlesticks(str_data) -> npt.NDArray[float32]:
  obj = json.loads(str_data)
  candlesticks: List[float32] = []
  for candlestick in obj["results"]:
    open = candlestick["o"]
    close = candlestick["c"]
    high = candlestick["h"]
    low = candlestick["l"]
    candlesticks.append(float32(open))
    candlesticks.append(float32(close))
    candlesticks.append(float32(high))
    candlesticks.append(float32(low))
  return array(candlesticks)

class Candle():
  FIRST = 0
  SECOND = 1
  THIRD = 2
  STOPLOSS = -1
  EMA = -1
  CONSTANT = -1
  INVESTED_PROPORTION = -1

class Attribute():
  OPEN = 0
  CLOSE = 1
  HIGH = 2
  LOW = 3
  STOPLOSS = -1
  EMA = 0
  CONSTANT = 1
  INVESTED_PROPORTION = 2

class Bound():
  LOWER = 0
  UPPER = 1


def create_rulebook(
  trade_proportions: List[float],
  candlesticks_per_rule: int,
  information: List[Tuple[int, Tuple[int, int, int], Tuple[int, int], float]]
):
  """
  information: [
    rule_index, 
    [candlestick_index, attribute_index, lower/upper]
      or [-1, -1, lower/upper] - stoploss, 
    [candlestick_index_2, attribute_index_2] 
      or [-1, 0] - ema 
      or [-1, 1] - constant 
      or [-1, 2] - invested_proportion
    set_value
  ]
  """
  inf: float = 999_999
  number_of_rules: int = len(trade_proportions)
  one_rule: int = (4 * candlesticks_per_rule + 3) * (8 * candlesticks_per_rule + 1) + 1
  size: int = number_of_rules * one_rule
  rulebook: npt.NDArray[float32] = zeros((size), dtype = float32)
  for i in range(len(trade_proportions)):
    rulebook[i * one_rule + one_rule - 1] = trade_proportions[i]
    for j in range(candlesticks_per_rule):
      for k in range(4):
        rulebook[i * one_rule + (4 * candlesticks_per_rule + 3) * (8 * j + 2 * k) + 4 * candlesticks_per_rule + 1] = -inf
        rulebook[i * one_rule + (4 * candlesticks_per_rule + 3) * (8 * j + 2 * k + 1) + 4 * candlesticks_per_rule + 1] = +inf
  for info in information:
    base: int = info[0] * one_rule
    if info[1][0] == -1:
      base += (4 * candlesticks_per_rule + 3) * (8 * candlesticks_per_rule)
    else:
      base += (4 * candlesticks_per_rule + 3) * (8 * info[1][0])
      base += (4 * candlesticks_per_rule + 3) * (2 * info[1][1])
    if info[1][2] == 1:
      base += (4 * candlesticks_per_rule + 3)
    offset: int = 0
    if info[2][0] == -1:
      offset += 4 * candlesticks_per_rule
    else:
      offset += 4 * info[2][0]
    offset += info[2][1]
    rulebook[base + offset] = info[3]
  return rulebook

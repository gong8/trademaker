from typing import List, Tuple, Type, TypeVar
from datetime import datetime
from werkzeug.datastructures import MultiDict
from numpy import zeros, float32, array
import numpy.typing as npt
import re
import json

def parse_date(date_str: str) -> datetime:
  """
  Convert a string in the format `yyyy-mm-dd` or `yyyy/mm/dd` into a `datetime` object.

  ### Parameters
  - date_str : str
    - The str to be converted.
    - It must be in the format `yyyy-mm-dd` or `yyyy/mm/dd`.

  ### Returns
  - datetime
    - The python `datetime` object represented by the string.

  ### Raises
  - ValueError* (Not implemented yet)
    - If the date string is not of one of the two expected formats.
  """
  
  parts = re.split("[/\\-]", date_str)
  if len(parts) != 3:
    raise RuntimeError("Invalid date format")
  year = int(parts[0])  
  month = int(parts[1])  
  day = int(parts[2])  
  return datetime(year, month, day)
  
def str_date(date: datetime) -> str:
  """
  Convert a `datetime` object into a string format for the polygon API.

  ### Parameters
  - date : datetime
    - The date to be converted.

  ### Returns
  - str
    - The string in the format `yyyy-mm-dd`.
  """

  return f"{date.year}-{str(date.month).zfill(2)}-{str(date.day).zfill(2)}"

T = TypeVar('T')
def get_param(args: MultiDict[str, str], key: str, name: str, type: Type[T]) -> T:
  """
  Check whether a key exists on a GET request, and return its value.

  ### Parameters
  - args : MultiDict[str, str]
    - The args object from from the flask request.
  - key : str
    - The key of the value in the args dictionary
  - name : str
    - The human-readable name of the key.
  - type : Type[T]
    - The data type of the key.

  ### Returns
  - T
    - This is the value of the key in the params, assuming it exists.

  ### Raises
  - ValueError
    - If the key does not exist in the args dictionary.
  """

  value = args.get(key, None, type)
  if value == None:
    raise ValueError(f"{name} not specified.")
  return value


def parse_candlesticks(str_data: str) -> npt.NDArray[float32]:
  """
  Parse data returned from the polygon API into a `numpy` array of candlesticks.

  ### Parameters
  - str_data : str
    - The data received from the polygon API, as a string. 

  ### Returns
  - npt.NDArray[float32]
    - This is the concatenation of the `[open, close, high, low]` of each candlestick.

  ### Raises
  - ValueError* (Not implemented yet)
    - If the string does not meet the polygon format of candlesticks data.
  """

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
  """
  For use in creating rulebooks, whenever a candlestick is required.
  """

  FIRST = 0
  SECOND = 1
  THIRD = 2
  STOPLOSS = -1
  EMA = -1
  CONSTANT = -1
  INVESTED_PROPORTION = -1

class Attribute():
  """
  For use in creating rulebooks, whenever an attribute is required.
  """

  OPEN = 0
  CLOSE = 1
  HIGH = 2
  LOW = 3
  STOPLOSS = -1
  EMA = 0
  CONSTANT = 1
  INVESTED_PROPORTION = 2

class Bound():
  """
  For use in creating rulebooks, whenever a bound is required.
  """

  LOWER = 0
  UPPER = 1

def create_rulebook(
  trade_proportions: List[float32],
  candlesticks_per_rule: int,
  information: List[Tuple[int, Tuple[int, int, int], Tuple[int, int], float32]]
) -> npt.NDArray[float32]:
  """
  Create a sparse rulebook from the given information.

  ### Parameters
  - trade_proportion : List[float32]
    - A list of trade proportions between `-1.0` and `1.0`.
    - `-1.0` means sell all stock owned.
    - `1.0` means buy as much stock as possible.
    - Any other values mean to do a proportion of one of the top two, depending on its sign.
  - candlesticks_per_rule : int
    - The number of prior candlesticks which each rule depends upon.
  - information : List[Tuple[int, Tuple[int, int, int], Tuple[int, int], float32]]
    - A list of entries to fill in the rulebook.
    - By default, the lower bound of everything is `-inf` and the upper bound is `+inf`.
    - The first in each tuple is the rule index.
    - The second in each tuple is the attribute whose condition is being changed.
    - - This first in this tuple is the candlestick index, or `-1` for other attributes.
    - - The second in this tuple is the attribute index.
    - - The third in this tuple is `0` for the lower bound and `1` for the upper bound.
    - The third in each tuple is the attribute whose coefficient is being changed.
    - - The first in this tuple is the candlestick index, or `-1` for other attributes.
    - - The second in this tuple is the attribute index.
    - The fourth in each tuple is the coefficient value to be set.

  ### Returns
  - npt.NDArray[float32]
      - The rulebook, which can be passed into the simulation functions.

  ### Raises
  - ValueError* (Not implemented yet)
      - If any of the values provided are out of bounds or otherwise invalid.
  """

  inf: float32 = float32(999_999)
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

# default rulebook
standard_rulebook = rulebook = create_rulebook(
    [float32(0.2), float32(-0.2)],
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
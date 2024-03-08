from typing import List
from numpy import float16, ndarray
import numpy.typing as npt

"""
n : number of candlesticks, (n = 5)
k : proportion to buy/sell (-sell, +buy), -1 <= k <= 1
v : a vector of size ?, 0 <= i < n
==> v[i*2] = the lower boundary of the open of the i-th candlestick from the left, of size 4i+3
==> v[i*2+1] = the upper boundary of the open of the i-th candlestick from the left, of size 4i+3
==> v[i*2+2] = the lower boundary of the close of the i-th candlestick from the left, of size 4i+3
==> v[i*2+3] = the upper boundary of the close of the i-th candlestick from the left, of size 4i+3
==> v[i*2+...] = the ...
==> v[i*2+7] = the upper boundary of the low of the i-th candlestick from the left, of size 4i+3
==> v[n*8] = the stop loss, of size 4n+3

each parameter-vector has:
open1, close1, high1, low1, ..., openX, closeX, highX, lowX, EMA, C, P
EMA = exponential moving average
C = constant
P = proportion of money in stock (0 <= P <= 1)

N = number of rules (N = 2)
S = size of v = ?
rulebook = NS = ?

simulate on [[open,close,high,low]]
"""


def simulate(
  candlesticks: npt.NDArray[float16], 
  rulebook: npt.NDArray[float16], 
  invested_units: float16, 
  available_money: float16,
  candlesticks_per_rule: int,
  rule_count: int,
  EMA_width: int,
):
  # precondition: EMA_width >= candlesticks_per_rule
  if EMA_width < candlesticks_per_rule:
    raise RuntimeError("EMA_width must be more than candlesticks_per_rule")

  # get initial values
  smooth: float = 2 / (1 + EMA_width)
  rule_length: int = len(rulebook) / rule_count
  start: float = invested_units * candlesticks[0] + available_money
  EMA: float = 0
  
  # initialise EMA
  for i in range(EMA_width):
    EMA += candlesticks[i*4+1]
  EMA /= EMA_width
  
  # simulate from EMA_width onwards
  for i in range(EMA_width, len(candlesticks)):
    trade_proportion: float = 0 # -1 <= trade_proportion <= 1
    invested_money: float = invested_units * candlesticks[i*4]
    invested_proportion: float = invested_money / (invested_money + available_money)
    for j in range(rule_count): # j-th rule in rulebook
      rule_satisfied: bool = True
      for k in range(candlesticks_per_rule): # k-th candlestick from left
        left_candle: int = (i-candlesticks_per_rule+1)*4
        right_candle: int = left_candle + k*4 + 4
        values: npt.NDArray[float16] = candlesticks[left_candle:right_candle] + [EMA, 1, invested_proportion]
        for l in range(4): # l-th attribute of k-th candlestick
          # [left_index, middle_index) -> vector of lower boundary rule
          # [middle_index, right_index) -> vector of upper boundary rule
          left_index: int = j*rule_length + 16*k**2 + 8*k + 4*l**2 + 2*l
          middle_index: int = left_index + 4*k + 3
          right_index: int = middle_index + 4*k + 3
          lower_coeff: npt.NDArray[float16] = rulebook[left_index:middle_index]
          upper_coeff: npt.NDArray[float16] = rulebook[middle_index:right_index]
          attribute: float = candlesticks[right_candle-1+l]
          if attribute < lower_coeff.dot(values) or attribute > upper_coeff.dot(values):
            rule_satisfied = False
      if rule_satisfied:
        trade_proportion += rulebook[j*rule_length+rule_length-1]
    if trade_proportion > 0:
      # buy stock
      trade_proportion = min(trade_proportion, 1)
      invested_units += trade_proportion * available_money / candlesticks[i*4+1]
      available_money *= 1 - trade_proportion
    else:
      # sell stock
      trade_proportion = min(-trade_proportion, 1)
      available_money += trade_proportion * invested_units * candlesticks[i*4+1]
      invested_units *= 1 - trade_proportion
    # update EMA
    EMA = candlesticks[i*4+1] * smooth + EMA * (1 - smooth)

  # calculate profit
  end: float = invested_units * candlesticks[len(candlesticks)-4+1] + available_money
  return end - start

# very good boris
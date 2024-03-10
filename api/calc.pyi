from typing import List, Tuple
from numpy import float32
from numpy.typing import NDArray

def simulate(
  candlesticks: NDArray[float32],
  rulebook: NDArray[float32], 
  invested_units: float32, 
  available_money: float32,
  candlesticks_per_rule: int,
  rule_count: int,
  EMA_width: int
) -> float32:
  """
  Highly optimised simulate function for ML training.

  ### Parameters
  - candlesticks : NDArray[float32]
    - The concatenation of `[open, close, high, low]` for all candlesticks.
  - rulebook : NDArray[float32]
    - The rulebook, as generated by `create_rulebook` or by AI.
  - invested_units : float32
    - The number of units of stock at the start of the trading period.
  - available_money : float32
    - The amount of money in the wallet at the start of the trading period, in USD.
  - candlesticks_per_rule : int
    - The number of prior candlesticks which each rule uses to decide its outcome. 
  - rule_count : int
    - The number of rules in the rulebook.
  - EMA_width : int
    - The width of the EMA window.

  ### Preconditions
  - `EMA_width` >= `candlesticks_per_rule`
    - This ensures the EMA is known before the first trade decision is made.

  ### Returns:
  - float32
    - The profit made over this trading period, using the rulebook.
  """

  pass

def simulate_detail(
  candlesticks: NDArray[float32],
  rulebook: NDArray[float32], 
  invested_units: float32, 
  available_money: float32,
  candlesticks_per_rule: int,
  rule_count: int,
  EMA_width: int
) -> List[Tuple[float32, float32]]:
  """
  Slower simulate function which returns more information about the trades which were made.

  ### Parameters
  - candlesticks : NDArray[float32]
    - The concatenation of `[open, close, high, low]` for all candlesticks.
  - rulebook : NDArray[float32]
    - The rulebook, as generated by `create_rulebook` or by AI.
  - invested_units : float32
    - The number of units of stock at the start of the trading period.
  - available_money : float32
    - The amount of money in the wallet at the start of the trading period, in USD.
  - candlesticks_per_rule : int
    - The number of prior candlesticks which each rule uses to decide its outcome. 
  - rule_count : int
    - The number of rules in the rulebook.
  - EMA_width : int
    - The width of the EMA window.

  ### Preconditions
  - `EMA_width` >= `candlesticks_per_rule`
    - This ensures the EMA is known before the first trade decision is made.

  ### Returns:
  - List[Tuple[float32, float32]]
    - A list of tuples of `invested_units` and `available_money` after each candlestick.
  """
  
  pass
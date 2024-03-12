import cython
import numpy as np

# https://cython.readthedocs.io/en/latest/src/userguide/memoryviews.html#syntax
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
@cython.cdivision(True)
def simulate(
  float[:] candlesticks,
  float[:] rulebook, 
  float invested_units, 
  float available_money,
  int candlesticks_per_rule,
  int rule_count,
  int EMA_width
):
  cdef float smooth, start, EMA, trade_proportion, invested_money, invested_proportion, attribute, lower_bound, upper_bound, end
  cdef int rule_length, i, j, k, l, m, left_candle, left_index, right_index, rule_satisfied

  # precondition: EMA_width >= candlesticks_per_rule
  if EMA_width < candlesticks_per_rule:
    raise ValueError("Error")

  # get initial values
  smooth = 2 / (1 + EMA_width)
  start = invested_units * candlesticks[0] + available_money
  EMA = 0
  rule_length = rulebook.shape[0] // rule_count
  
  # initialise EMA
  for i in range(EMA_width):
    EMA += candlesticks[i*4+1]
  EMA /= EMA_width
  
  # simulate from EMA_width onwards
  for i in range(EMA_width, candlesticks.shape[0] // 4):
    trade_proportion = 0 # -1 <= trade_proportion <= 1
    invested_money = invested_units * candlesticks[i*4]
    invested_proportion = invested_money / (invested_money + available_money)
    left_candle = (i - candlesticks_per_rule + 1) * 4
    for j in range(rule_count): # j-th rule in rulebook
      rule_satisfied = True
      for k in range(candlesticks_per_rule): # k-th candlestick from left
        for l in range(4): # l-th attribute of k-th candlestick
          left_index = j * rule_length + (4 * candlesticks_per_rule + 3) * (8 * k + 2 * l)
          right_index = left_index + 4 * candlesticks_per_rule + 3
          
          # dot product cuz numpy can't do it
          lower_bound = 0
          for m in range(4 * candlesticks_per_rule):
            lower_bound += rulebook[left_index + m] * candlesticks[left_candle + m]
          lower_bound += rulebook[left_index + 4 * candlesticks_per_rule] * EMA
          lower_bound += rulebook[left_index + 4 * candlesticks_per_rule + 1]
          lower_bound += rulebook[left_index + 4 * candlesticks_per_rule + 2] * invested_proportion
          
          # dot product cuz numpy can't do it
          upper_bound = 0
          for m in range(4 * candlesticks_per_rule):
            upper_bound += rulebook[right_index + m] * candlesticks[left_candle + m]
          upper_bound += rulebook[right_index + 4 * candlesticks_per_rule] * EMA
          upper_bound += rulebook[right_index + 4 * candlesticks_per_rule + 1]
          upper_bound += rulebook[right_index + 4 * candlesticks_per_rule + 2] * invested_proportion
          
          attribute = candlesticks[left_candle + 4 * k + l]
          if attribute < lower_bound or attribute > upper_bound:
            rule_satisfied = False
      if rule_satisfied:
        trade_proportion += rulebook[j * rule_length + rule_length - 1]
    if trade_proportion > 0:
      # buy stock
      trade_proportion = min(trade_proportion, 1.0)
      invested_units += trade_proportion * available_money / candlesticks[i * 4 + 1]
      available_money *= 1 - trade_proportion
    else:
      # sell stock
      trade_proportion = min(-trade_proportion, 1.0)
      available_money += trade_proportion * invested_units * candlesticks[i * 4 + 1]
      invested_units *= 1 - trade_proportion
    # update EMA
    EMA = candlesticks[i * 4 + 1] * smooth + EMA * (1 - smooth)

  # calculate profit
  end = invested_units * candlesticks[candlesticks.shape[0] - 4 + 1] + available_money
  return end - start

def simulate_detail(
  float[:] candlesticks,
  float[:] rulebook, 
  float invested_units, 
  float available_money,
  int candlesticks_per_rule,
  int rule_count,
  int EMA_width
):
  cdef float smooth, EMA, trade_proportion, invested_money, invested_proportion, attribute, lower_bound, upper_bound
  cdef int rule_length, i, j, k, l, m, left_candle, left_index, right_index, rule_satisfied

  # precondition: EMA_width >= candlesticks_per_rule
  if EMA_width < candlesticks_per_rule:
    raise ValueError("Error")

  # get initial values
  smooth = 2 / (1 + EMA_width)
  EMA = 0
  rule_length = rulebook.shape[0] // rule_count
  
  # create output list
  cdef float[:] invested_units_list, available_money_list
  invested_units_list = np.zeros((candlesticks.shape[0] // 4), np.float32)
  available_money_list = np.zeros((candlesticks.shape[0] // 4), np.float32)

  # initialise EMA
  for i in range(EMA_width):
    EMA += candlesticks[i*4+1]
    invested_units_list[i] = invested_units
    available_money_list[i] = available_money
  EMA /= EMA_width
  
  # simulate from EMA_width onwards
  for i in range(EMA_width, candlesticks.shape[0] // 4):
    trade_proportion = 0 # -1 <= trade_proportion <= 1
    invested_money = invested_units * candlesticks[i*4]
    invested_proportion = invested_money / (invested_money + available_money)
    left_candle = (i - candlesticks_per_rule + 1) * 4
    for j in range(rule_count): # j-th rule in rulebook
      rule_satisfied = True
      for k in range(candlesticks_per_rule): # k-th candlestick from left
        for l in range(4): # l-th attribute of k-th candlestick
          left_index = j * rule_length + (4 * candlesticks_per_rule + 3) * (8 * k + 2 * l)
          right_index = left_index + 4 * candlesticks_per_rule + 3
          
          # dot product cuz numpy can't do it
          lower_bound = 0
          for m in range(4 * candlesticks_per_rule):
            lower_bound += rulebook[left_index + m] * candlesticks[left_candle + m]
          lower_bound += rulebook[left_index + 4 * candlesticks_per_rule] * EMA
          lower_bound += rulebook[left_index + 4 * candlesticks_per_rule + 1]
          lower_bound += rulebook[left_index + 4 * candlesticks_per_rule + 2] * invested_proportion
          
          # dot product cuz numpy can't do it
          upper_bound = 0
          for m in range(4 * candlesticks_per_rule):
            upper_bound += rulebook[right_index + m] * candlesticks[left_candle + m]
          upper_bound += rulebook[right_index + 4 * candlesticks_per_rule] * EMA
          upper_bound += rulebook[right_index + 4 * candlesticks_per_rule + 1]
          upper_bound += rulebook[right_index + 4 * candlesticks_per_rule + 2] * invested_proportion
          
          attribute = candlesticks[left_candle + 4 * k + l]
          if attribute < lower_bound or attribute > upper_bound:
            rule_satisfied = False
      if rule_satisfied:
        trade_proportion += rulebook[j * rule_length + rule_length - 1]
    if trade_proportion > 0:
      # buy stock
      trade_proportion = min(trade_proportion, 1.0)
      invested_units += trade_proportion * available_money / candlesticks[i * 4 + 1]
      available_money *= 1 - trade_proportion
    else:
      # sell stock
      trade_proportion = min(-trade_proportion, 1.0)
      available_money += trade_proportion * invested_units * candlesticks[i * 4 + 1]
      invested_units *= 1 - trade_proportion
    # update EMA
    EMA = candlesticks[i * 4 + 1] * smooth + EMA * (1 - smooth)
    # add to output
    invested_units_list[i] = invested_units
    available_money_list[i] = available_money

  # join into list of tuples
  return list(zip(invested_units_list, available_money_list))

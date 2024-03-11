from numpy import float32
from helper import create_rulebook, Candle, Attribute, Bound, parse_date, parse_candlesticks
from calc import simulate_detail
from polygon import get_data

if __name__ == "__main__":
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
  str_data = get_data("AAPL", 1, "minute", parse_date("2023-01-03"), parse_date("2023-02-02"))
  candlesticks = parse_candlesticks(str_data)
  # we require starting stocks, starting money
  result = simulate_detail(
    candlesticks,
    rulebook,
    float32(100),
    float32(10_000),
    3,
    2,
    10
  )
  print(result)

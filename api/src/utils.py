from datetime import datetime
import re

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

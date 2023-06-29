from datetime import datetime, timedelta
from django.utils import timezone
import calendar
import re

def subtract_months(date, num_months):
    month = date.month - 1 - num_months
    year = date.year + month // 12
    month = month % 12 + 1
    day = min(date.day, calendar.monthrange(year, month)[1])
    return datetime(year, month, day)

def convert_date_format(date_str):
    
    if date_str.lower() == "today":
        return timezone.now()

    if "d" in date_str.lower() or "day" in date_str.lower():
        try:
            days_ago = int(re.search(r'(\d+)', date_str).group())
            target_date = timezone.now() - timedelta(days=days_ago)
            return target_date
        except (ValueError, AttributeError):
            raise ValueError("Invalid format for days ago")

    if "m" in date_str.lower() or "month" in date_str.lower():
        try:
            months_ago = int(re.search(r'(\d+)', date_str).group())
            target_date = subtract_months(timezone.now(), months_ago)
            return target_date
        except (ValueError, AttributeError):
            raise ValueError("Invalid format for months ago")

    formats =  [
        "%Y-%m-%d",             # YYYY-MM-DD
        "%Y-%d-%m",             # YYYY-DD-MM
        "%d-%m-%Y",             # DD-MM-YYYY
        "%m-%d-%Y",             # MM-DD-YYYY
        "%Y-%m-%dT%H:%M:%S",    # ISO 8601 / RFC 3339 without timezone
        "%Y-%m-%dT%H:%M:%S%z",  # ISO 8601 / RFC 3339 with timezone
        "%b %d, %Y",            # Month abbreviation followed by day and year: Jun 15, 2023
        "%d %b %Y",             # Day followed by month abbreviation and year: 15 Jun 2023
        "%b %d %Y",             # Month abbreviation followed by day and year without comma: Jun 15 2023
        "%Y/%m/%d",             # YYYY/MM/DD
        "%Y/%d/%m",             # YYYY/DD/MM
        "%m/%d/%Y",             # MM/DD/YYYY
        "%d/%m/%Y",             # DD/MM/YYYY
        
        "%Y.%m.%d",             # YYYY.MM.DD
        "%Y.%d.%m",             # YYYY.DD.MM
        "%d.%m.%Y",             # DD.MM.YYYY
        "%m.%d.%Y",             # MM.DD.YYYY
        "%Y %b %d",             # YYYY Jun 15
        "%Y %b. %d",            # YYYY Jun. 15
        "%Y %B %d",             # YYYY June 15
        "%Y-%b-%d",             # YYYY-Jun-15
        "%Y-%B-%d",             # YYYY-June-15
        "%d %b %Y",             # 15 Jun 2023
        "%d %b. %Y",            # 15 Jun. 2023
        "%d %B %Y",             # 15 June 2023
        "%d-%b-%Y",             # 15-Jun-2023
        "%d-%B-%Y",             # 15-June-2023
        "%d/%b/%Y",             # 15/Jun/2023
        "%d/%B/%Y",             # 15/June/2023
    ]

    for date_format  in formats:
        try:
            return datetime.strptime(date_str, date_format)
            # input_date = datetime.strptime(date_str, date_format).date()
            # return input_date.strftime("%Y-%M-%D")
        except ValueError:
            continue

    raise ValueError("Invalid date format. Please provide a valid date string.")
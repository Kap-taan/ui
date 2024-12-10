from datetime import date, datetime
import pytz

def convert_to_utc(local_date, local_timezone):
    # Convert `date` to a `datetime` with time at midnight (00:00:00)
    local_datetime = datetime.combine(local_date, datetime.min.time())

    # Localize the datetime to the provided timezone
    local_tz = pytz.timezone(local_timezone)
    localized_time = local_tz.localize(local_datetime)

    # Convert to UTC
    utc_time = localized_time.astimezone(pytz.utc)
    return utc_time.strftime("%Y-%m-%d %H:%M:%S")

# Example usage
# date_obj = date.today()  # Local date (without time)
# print("Original Date (Local):", date_obj)

# local_timezone = "Mexico/BajaSur"  # Example timezone
# utc_time = convert_to_utc(date_obj, local_timezone)

# Convert to string with time component
# utc_time_str = utc_time.strftime("%Y-%m-%d %H:%M:%S")
# print(f"UTC Time: {utc_time_str}")
